import math
from QuizzMainClass import Quizz
import numpy as np
import pandas as pd
import collections, math

class BertrandDuopoly(Quizz):

    def head_action_info(self, action, action_list):
        actions = [action]
        frequencies = ['%']
        hist, edges = np.histogram(action_list, bins = [0, 10, 20, 30, 40, 50, 60, 100])
        for i in range(len(hist)):
            actions.append(str(edges[i])+'-'+str(edges[i+1]))
            frequencies.append(self.percentage(hist[i]/len(action_list)))
        return actions, frequencies    

    def create_action_names(self):
        self.action_names = {'What is your':'*'}

    def payoff(self, strategy1, strategy2):
        action1 = int(strategy1['*'])
        action2 = int(strategy2['*'])
        if action1 < action2: return action1
        if action1 == action2: return action1/2
        return 0
    
    def set_max_min_payoff(self):
        max = 100
        min = 0
        return max, min

class InvestmentGameI(Quizz):

    def create_action_names(self):
        self.action_names = {'What action do you choose':'*'}

    def payoff(self, strategy1, strategy2):
        action1 = strategy1['*']
        action2 = strategy2['*']
        if action1 == 'Invest' and action2 == 'Invest': return 1
        if action1 == 'Invest' and action2 != 'Invest': return -2
        return 0
    
    def set_max_min_payoff(self):
        max = 1
        min = 0
        return max, min

class InvestmentGameII(Quizz):

    def is_strategy_legitimate(self, strategy):
        legitimate = False
        for action in strategy:
            if not pd.isna(strategy[action]): legitimate = True
        return legitimate

    def head_action_info(self, action, action_list):
        action_list = [a for a in action_list if isinstance(a, str) or not math.isnan(a)]
        if action in {'D', 'I'}:
            if action == 'D': actions = ["expected Don't Invest"]
            else: actions = ["expected Invest"]
            frequencies = ['%']
            counter = collections.Counter(action_list)
            for key,value in counter.most_common():
                if isinstance(key, str) or not math.isnan(key):
                    actions.append(key)
                    frequencies.append(self.percentage(value/len(action_list)))
            """"    
            hist, edges = np.histogram(action_list, bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
            for i in range(len(hist)):
                actions.append(str(edges[i])+'-'+str(edges[i+1]))
                frequencies.append(self.percentage(hist[i]/len(action_list)))
            """
            return actions, frequencies
        else:
            return super().head_action_info(action, action_list)
        
    def set_max_min_payoff(self):
        max = 1
        min = 0
        return max, min

    def create_action_names(self):
        self.action_names = {'will choose to Invest':'I', 'will choose not to Invest':'D'}

    def payoff(self, strategy1, strategy2):
        if strategy1['I'] in ['Invest', "Don't Invest"] and strategy2['I'] in ['Invest', "Don't Invest"]:
            m = 'I'
        elif strategy1['D'] in ['Invest', "Don't Invest"] and strategy2['D'] in ['Invest', "Don't Invest"]:
            m = 'D'
        else: return 0
        action1 = strategy1[m]
        action2 = strategy2[m]
        if action1 == 'Invest' and action2 == 'Invest': return 1
        if action1 == 'Invest' and action2 != 'Invest': return -2
        return 0

class StockMarket(Quizz):

    def head_action_info(self, action, action_list):
        if action == '*':
            actions = [action]
            frequencies = ['%']
            hist, edges = np.histogram(action_list, bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
            for i in range(len(hist)):
                actions.append(str(edges[i])+'-'+str(edges[i+1]))
                frequencies.append(self.percentage(hist[i]/len(action_list)))
            return actions, frequencies
        else:
            return super().head_action_info(action, action_list)

    def is_strategy_legitimate(self, strategy):
        action_raw = strategy['*']
        return isinstance(action_raw, (int, float)) and not math.isnan(action_raw)

    def create_action_names(self):
        self.action_names = {'Choose any number':'*'}

    def compute_payoffs(self):
        #find 5th largest action
        actions_raw = [student.quizzes[self.name]['strategy']['*'] for student in self.students.values()]
        actions = [int(action_raw) for action_raw in actions_raw]
        actions.sort(reverse=True)
        threshold = actions[4] - 10
        for student in self.students.values():
            action = int(student.quizzes[self.name]['strategy']['*'])
            payoff = action - 10 * max(action - threshold, 0)
            student.quizzes[self.name]['payoff'] = payoff

    def set_max_min_payoff(self):
        max = 90
        min = -100
        return max, min

class StockMarketII(StockMarket):

    def create_action_names(self):
        self.action_names = {'Choose any action':'*', 'prediction':'prediction'}

class Schelling(Quizz):

    def create_action_names(self):
        self.action_names = {'partner lives in Toronto':'Toronto', 'University':'UofT'}

    def compute_strategy(self, row):
        strategy = {action: row[self.column_name[action]] for action in self.column_name}
        map = {'Robarts Library': {'Robart', "robert", 'rb'},
                'University College': {'uc', 'university college'},
                'CN Tower': {'CN'},
                'Bahen Centre': {'Bahen'},
                'Sidney Smith Hall': {'Sid', 'sidney' 'smith'}, 
                'Eaton Centre': {'Eaton'},
                }
        for a in strategy:
            for action in map:
                for key in map[action]:
                    if key.lower() in strategy[a].lower(): strategy[a] = action
        return strategy

    def payoff(self, strategy1, strategy2):
        p = 0
        if strategy1['Toronto'] == strategy2['Toronto']: p +=1
        if strategy1['UofT'] == strategy2['UofT']: p +=1
        return p/2
    
    def set_max_min_payoff(self):
        max = 1
        min = 0
        return max, min
    
class Duel(Quizz):

    def head_action_info(self, action, action_list):
        actions = [action]
        frequencies = ['%']
        hist, edges = np.histogram(action_list, bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        for i in range(len(hist)):
            actions.append(str(edges[i])+'-'+str(edges[i+1]))
            frequencies.append(self.percentage(hist[i]/len(action_list)))
        return actions, frequencies    

    def create_action_names(self):
        self.action_names = {'When will you shoot':'*'}

    def payoff(self, strategy1, strategy2):
        a = int(strategy1['*'])
        b = int(strategy2['*'])
        m = min(a,b)
        payoff = 1 - ((101 - m)/100)**2
        if a < b: return payoff
        else: return 1 - payoff

    def set_max_min_payoff(self):
        max = 1
        min = 0
        return max, min

class Hotelling(Quizz):

    def create_action_names(self):
        self.action_names = {'platform':'*'}

    def payoff(self, strategy1, strategy2):
        a = int(strategy1['*'])
        b = int(strategy2['*'])
        voters = [1, 2, 3, 4, 3, 3, 1, 1, 1, 1, 1]
        payoff = 0
        for i in range(len(voters)):
            if abs(a-i) < abs(b-i): payoff += voters[i]
            if abs(a-i) == abs(b-i): payoff += 0.5*voters[i]
        return payoff
    
    def set_max_min_payoff(self):
        max = 20
        min = 0
        return max, min

class GrabDollar(Quizz):

    def create_action_names(self):
        self.action_names = {'When do you stop':'*'}

    def payoff(self, strategy1, strategy2):
        a = int(strategy1['*'])
        b = int(strategy2['*'])
        if a<b: return 4 + a
        if a>b: return b
        return 2+a
    
    def set_max_min_payoff(self):
        max = 100
        min = 0
        return max, min

class BattleSexesIncomplete(Quizz):

    def create_action_names(self):
        self.action_names = {'Bob':'B', 'Alice type meet':'m', 'Alice type avoid':'a'}

    def payoff_Alice(self,a,b,t):
        if t=='m':
            if a == b and a == 'Opera': return 5
            if a == b: return 3
            return 0
        if a != b and a == 'Opera': return 5
        if a != b: return 3
        return 0

    def payoff_Bob(self, a,b,t):
        if a == b and a == 'Stadium': return 5
        if a == b: return 3
        return 0

    def payoff(self, strategy1, strategy2):
        payoff = 1/2 * self.payoff_Alice(strategy1['a'],strategy2['B'],'a')
        payoff += 1/2 * self.payoff_Alice(strategy1['m'],strategy2['B'],'m')
        payoff += 1/2 * self.payoff_Bob(strategy2['a'],strategy1['B'],'a')
        payoff += 1/2 * self.payoff_Bob(strategy2['m'],strategy1['B'],'m') 
        return payoff/2
    
    def set_max_min_payoff(self):
        max = 5
        min = 0
        return max, min

class FinitelyRepeated(Quizz):

    def create_action_names(self):
        self.action_names = {'Defect':'*'}

    def payoff(self, strategy1, strategy2):
        a = int(strategy1['*'])
        b = int(strategy2['*'])
        m = min(a,b)
        if a<b: return (a-1)*2 + 3
        if a==b: return (a-1)*2
        return (b-1)*2 - 10
    
    def set_max_min_payoff(self):
        max = 200
        min = 0
        return max, min

class TrafficGame(Quizz):

    def create_action_names(self):
        self.action_names = {'you are the Police Officer':'p', 'you are the Driver':'d'}

    def basic_payoff_police(self,p,d):
        if p == 'Patrol' and d == 'Speed': return 1
        if p == 'Patrol' and d == 'Obey': return -1
        if p == 'Relax' and d == 'Speed': return 0
        if p == 'Relax' and d == 'Obey': return 0
    
    def basic_payoff_driver(self,p,d):
        if p == 'Patrol' and d == 'Speed': return -2
        if p == 'Patrol' and d == 'Obey': return 0
        if p == 'Relax' and d == 'Speed': return 2
        if p == 'Relax' and d == 'Obey': return 0

    def payoff(self, strategy1, strategy2):
        payoff = self.basic_payoff_police(strategy1['p'], strategy2['d'])
        payoff +=  self.basic_payoff_police(strategy2['p'], strategy1['d'])
        return payoff
    
    def set_max_min_payoff(self):
        max = 2
        min = 0
        return max, min

class StagHunt(Quizz):

    def create_action_names(self):
        self.action_names = {'What is your action':'*'}

    def compute_payoffs(self):
        actions = [student.quizzes[self.name]['strategy']['*'] for student in self.students.values()]
        if 'H' in actions:
            for student in self.students.values():
                a = student.quizzes[self.name]['strategy']['*']
                if a == 'H': student.quizzes[self.name]['payoff'] = 1
                if a == 'S': student.quizzes[self.name]['payoff'] = 0
        else:
            for student in self.students.values():
                a = student.quizzes[self.name]['strategy']['*']
                if a == 'H': student.quizzes[self.name]['payoff'] = 1
                if a == 'S': student.quizzes[self.name]['payoff'] = 2

    def set_max_min_payoff(self):
        max = 2
        min = 0
        return max, min

class MovieBattleSexes(Quizz):

    def create_action_names(self):
        self.action_names = {'Will you rent a Movie?':'Rent', "Alice, and you haven't rented a Movie":'Alice', "Bob and Alice hasn't rented":'Bob'}

    def basic_payoff_Alice(self, strategy1, strategy2):
        if strategy1['Rent'] == 'No':
            if strategy1['Alice'] == 'Opera' and strategy2['Bob'] == 'Opera': return 10
            if strategy1['Alice'] == 'Stadium' and strategy2['Bob'] == 'Stadium': return 3
            return 0
        else:
            return 5

    def basic_payoff_Bob(self, strategy1, strategy2):
        if strategy2['Rent'] == 'No':
            if strategy2['Alice'] == 'Opera' and strategy1['Bob'] == 'Opera': return 3
            if strategy2['Alice'] == 'Stadium' and strategy1['Bob'] == 'Stadium': return 10
            return 0
        else:
            return 0

    def payoff(self, strategy1, strategy2):
        payoff = self.basic_payoff_Alice(strategy1, strategy2) + self.basic_payoff_Bob(strategy1, strategy2) 
        return payoff
    
    def set_max_min_payoff(self):
        max = 15
        min = 0
        return max, min

class Ultimatum(Quizz):

    def create_action_names(self):
        self.action_names = {'Suppose that you are the offeror':'offer', "Suppose that you are an offeree.":'accept'}

    def basic_payoff_offeror(self, strategy1, strategy2):
        if strategy1['offer'] >= strategy2['accept']:
            return 100 - strategy1['offer']
        else:
            return 0

    def basic_payoff_offeree(self, strategy1, strategy2):
        if strategy2['offer'] >= strategy1['accept']:
            return strategy2['offer']
        else:
            return 0

    def payoff(self, strategy1, strategy2):
        payoff = self.basic_payoff_offeror(strategy1, strategy2) + self.basic_payoff_offeree(strategy1, strategy2) 
        return payoff
    
    def set_max_min_payoff(self):
        max = 100
        min = 0
        return max, min

class Raffle(Quizz):

    def create_action_names(self):
        self.action_names = {'How many tickets':'*'}

    def payoff(self, strategy1, strategy2):
        t1 = strategy1['*']
        if t1==0: return 0
        t2 = strategy2['*']
        payoff = t1* (100/(t1+t2) - 1) 
        return payoff
    
    def set_max_min_payoff(self):
        max = 100
        min = 0
        return max, min

class Auction(Quizz):

    def create_action_names(self):
        self.action_names = {'Q1':'Q1', 'Q2':'Q2', 'Q3':'Q3', 'Q4':'Q4', 'Q5':'Q5', 'Q6':'Q6'}

    def compute_strategy(self, row):
        strategy = {}
        for action in self.column_name:
            a = row[self.column_name[action]].split(',')
            if len(a) == 2 and '=>' in a[0]: 
                b = float(a[1])
                a = a[0].split('=>')
                v = round(float(a[1]))
                strategy[v] = b
        return strategy

    def basic_payoff(self, v1, b1, v2, b2):
        return 0

    def payoff(self, strategy1, strategy2):
        p = 0
        for v1 in strategy1:
            for v2 in strategy2:
                p += self.basic_payoff(v1, strategy1[v1], v2, strategy2[v2])
        return p

    def head_winning_info(self):
        return []

    def head_frequencies_info(self):
        vapairs = [[v, student.quizzes[self.name]['strategy'][v]] for student in self.students.values() for v in student.quizzes[self.name]['strategy']]
        vapairs.sort(key=lambda x: x[0])
        no_baskets = 10
        baskets = np.array_split(vapairs, no_baskets)
        baskets = [b for b in baskets if len(b)>0]
        no_baskets = len(baskets)
        if no_baskets>0:
            payoffsum = {i:sum([p[1] for p in baskets[i]]) for i in range(no_baskets)}
            no = {i:len([p[1] for p in baskets[i]]) for i in range(no_baskets)}
            average = {i:int(payoffsum[i]/no[i])  for i in range(no_baskets)}
            line1 = ['Valuation basket'] + [str(int(baskets[i][0][0]))+'-'+str(int(baskets[i][-1][0])) for i in range(no_baskets)]
            line2 = ['Average bid'] + [str(average[i]) for i in range(no_baskets)]
            return [line1, line2]   
        return []
    
    def set_max_min_payoff(self):
        max = 100
        min = 0
        return max, min

class FirstPriceAuction(Auction):

    def basic_payoff(self, v1, b1, v2, b2):
        if b1 > b2: 
            return v1 - b1
        if b1 == b2: 
            return 0.5* (v1 - b1)
        return 0

class TwoJars(Auction):

    def basic_payoff(self, v1, b1, v2, b2):
        if b1 > b2: 
            return v1 + v2 - b1
        if b1 == b2: 
            return 0.5* (v1 + v2 - b1)
        return 0
    
    def set_max_min_payoff(self):
        max = 100
        min = 0
        return max, min