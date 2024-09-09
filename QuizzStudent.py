from datetime import timedelta, datetime

class Student:

    def __init__(self, index, row, quizzes):
        self.index = index
        self.name = row['name']
        self.id = row['sis_id']
        self.quizzes = {q.name:{'quizz':q, 'row': '', 'submitted':'', 'participate':0,'on time':0} for q in quizzes}
        self.midterm = 0
        self.final = 0

    def __repr__(self):
        return self.name

    def add_quizz(self, quizz, row):
        date = row['submitted']
        date_submitted = datetime.strptime(row['submitted'], '%Y-%m-%d %H:%M:%S %Z')
        #on_time = int(date_submitted < quizz.due_date)
        on_time = True
        self.quizzes[quizz.name] = {'quizz':quizz, 'submitted':date_submitted, 'participate':1, 'on time':on_time}

    def to_report(self):
        line = {}
        line['name'] = self.name
        line['index'] = self.index
        line['total score'] = self.total_score()
        line['midterm'] = self.midterm
        line['final'] = self.final
        total = 0
        no = 0
        elines = {}
        for q_name in self.quizzes:
            no += 1
            quizz = self.quizzes[q_name]
            short_name = quizz['quizz'].short_name
            if quizz['submitted'] != '':
                date = quizz['submitted'].strftime("%m/%d, %H:%M")
            else:
                date = ''
            elines[str(no)+short_name+'S'] = date
            elines[str(no)+short_name+'O'] = quizz['on time']
            total += quizz['on time']
        line['# quizzes'] = total
        if total != 0: 
            line['av. score'] = round(line['total score']/total)
        else: 
            line['av. score'] = 0
        for key in elines:
            line[key] = elines[key]
        return line

    def to_report_scores(self):
        line = {}
        line['name'] = self.name
        line['index'] = self.index
        line['total score'] = self.total_score()
        total = 0
        no = 0
        for q_name in self.quizzes:
            no += 1
            quizz = self.quizzes[q_name]
            if quizz['on time']: 
                line[str(no)+quizz['quizz'].short_name] = quizz['score']
                total += 1
        line['# quizzes'] = total
        if total != 0: 
            line['av. score'] = round(line['total score']/total)
        else: 
            line['av. score'] = 0
        return line

    def report(self, quiz):
        line = {'name':self.name}
        for key, value in self.quizzes[quiz.name].items():
            if key != 'strategy':
                line[key] = value
            else:
                for path, action in value.items():
                    line[path] = action 
        return line

    def total_score(self):
        score = 0
        for quiz in self.quizzes:
            if self.quizzes[quiz]['participate'] == 1 and self.quizzes[quiz]['on time'] == 1:
                score += self.quizzes[quiz]['score']
        return score