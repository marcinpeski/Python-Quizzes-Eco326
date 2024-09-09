HIGH = 100000

from datetime import timedelta, datetime
import pandas as pd
import os
from config import *
from QuizzStudent import Student
import collections, math


class Quizz:

    def __init__(self, filename):
        self.filename = filename
        i=min(30, len(self.filename))
        for keyword in ['Survey', '(graded', '.', 'Quiz']:
            place = self.filename.find(keyword)
            if place != -1 and place <i: i = place
        self.name = self.filename[:i]
        self.short_name = self.name[0:10]
        self.students = {}
        self.due_date = datetime(2100, 3, 23, 3, 59)
        self.strategy = {}
        self.create_action_names()

    def __repr__(self):
        return self.name

    def load(self):
        file_with_path = os.path.join(quizz_directory, self.filename)
        self.df = pd.read_csv(file_with_path)
        self.df.dropna(subset=['submitted'])
        

    def read_students(self, students, quizzes):
        self.load_action_names()
        for row_tuple in self.df.iterrows():
            row = row_tuple[1]
            s_index = row['id']
            strategy = self.compute_strategy(row)
            if self.is_strategy_legitimate(strategy):
                if s_index in students:
                    student = students[s_index]
                else:
                    student = Student(s_index, row, quizzes)
                    students[s_index] = student
                student.add_quizz(self, row)
                self.add_student(student)
                student.quizzes[self.name]['strategy'] = strategy

    def compute_strategy(self, row):
        return {action: row[self.column_name[action]] for action in self.column_name}

    def add_student(self, student):
        self.students[student.index] = student

    def set_due_date(self, due_date):
        self.due_date = due_date

    def is_name(self, s):
        return s.lower() in self.name.lower()

    def is_strategy_legitimate(self, strategy):
        legitimate = True
        for action in strategy:
            if pd.isna(strategy[action]): legitimate = False
        return legitimate

    def analyze(self):
        self.compute_payoffs()
        self.scale_payoffs()
            
    def compute_payoffs(self):
        for student1 in self.students.values():
            payoff = 0
            for student2 in self.students.values():
                if student1 != student2:
                    payoff += self.payoff(student1.quizzes[self.name]['strategy'], student2.quizzes[self.name]['strategy'])
            student1.quizzes[self.name]['payoff'] = round(payoff/len(self.students),2)

    def payoff (self, strategy1, strategy2):
        pass

    def set_max_min_payoff(self):
        max_payoff = -HIGH
        min_payoff = HIGH
        for student in self.students.values():
            payoff = student.quizzes[self.name]['payoff']
            if payoff > max_payoff: max_payoff = payoff
            if payoff < min_payoff: min_payoff = payoff
        return max_payoff, min_payoff   

    def scale_payoffs(self):
        max, min = self.set_max_min_payoff()
        for student in self.students.values():
            payoff = student.quizzes[self.name]['payoff']
            if max>min:
                student.quizzes[self.name]['score'] = round(100*(payoff - min)/(max - min))
            else:
                student.quizzes[self.name]['score'] = 0

    def create_action_names(self):
        self.action_names = {}

    def load_action_names(self):
        self.column_name = {}
        for column in self.df.columns:
            for keyword,action in self.action_names.items():
                if keyword in column:
                    self.column_name[action] = column

    def head_info(self):
        max, min = self.set_max_min_payoff()
        head = [['#'*10]*10]
        head += [[self.name.upper(), self.due_date.strftime("%d %b %Y"), '', '', 'normalization',  '(for score computations):', '', 'max', max, 'min', min]]
        head += self.head_winning_info()
        head += self.head_frequencies_info()
        head += self.head_additional_info()
        return head

    def head_winning_info(self):
        head = []
        max_payoff = -1000000
        for student in self.students.values():
            payoff = student.quizzes[self.name]['payoff']
            if payoff > max_payoff:
                max_payoff = payoff
                max_strategies = [student.quizzes[self.name]['strategy']]
            elif payoff == max_payoff:
                strategy = student.quizzes[self.name]['strategy']
                if not strategy in max_strategies: max_strategies.append(strategy)
        head.append(['Winning payoffs: ', max_payoff])
        for strategy in max_strategies:
            line = ['Winning strategy: ']
            for action in strategy:
                name = action
                if name == '*': name = ''
                value = strategy[action]
                if isinstance(value, (float, int, str, list, dict, tuple)): value = str(value)
                line.append(name+' '+value)
            head.append(line)
        return head


    def head_action_info(self, action, action_list):
        actions = [action]
        frequencies = ['%']
        counter = collections.Counter(action_list)
        for key,value in counter.most_common():
            if isinstance(key, str) or not math.isnan(key):
                actions.append(key)
                frequencies.append(self.percentage(value/len(action_list)))
        return actions, frequencies  
    
    def head_frequencies_info(self):
        head = [['Frequencies: ']]
        for action in self.action_names.values():
            action_list = [student.quizzes[self.name]['strategy'][action] for student in self.students.values()]
            head += [*self.head_action_info(action, action_list)]
        return head

    def head_additional_info(self):
        return []

    def percentage(self, a):
        return str(round(100*a))+'%'