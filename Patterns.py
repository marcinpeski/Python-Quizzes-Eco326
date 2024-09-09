import sklearn, os, pandas as pd
import config
import math

class Column:

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.labels = {row['label'] for row in self.data.values()}
        self.actions = {row[self.name] for row in self.data.values()}
        self.params = {}

    def is_empty(self, row):
        a = row[self.name]
        return (type(a)==str and a=='') or (type(a)==float and math.isnan(a)) 

    def parameters(self):
        miss = {label:0 for label in self.labels}
        count = {label:0 for label in self.labels}
        for row in self.data.values():
            label,a = row['label'], row[self.name]
            if self.is_empty(row): miss[label] += 1
            count[label] += 1
        for label in self.labels:
            miss[label] = miss[label]/count[label]
        self.params['missing'] = miss
        self.params['count'] = count
    
    def ll(self, row):
        a = row[self.name]
        label = row['label']
        miss = self.params['missing']
        if self.is_empty(row): 
            return math.log(self.miss[label])
        else:
            return math.log(1-self.miss[label])

class GaussianColumn(Column):

    def parameters(self):
        super().parameters()
        average = {label:0 for label in self.labels}
        sigma = {label:0 for label in self.labels}
        count = self.params['count']
        for row in self.data.values():
            if not self.is_empty(row):
                label,a = row['label'], row[self.name]
                average[label] += a
                sigma[label] += a**2
        for label in self.labels:
            average[label] = average[label]/count[label]
            sigma[label] = ((sigma[label]-count[label]*(average[label])**2)/count[label])**(1/2)
        self.params['average'] = average
        self.params['sigma'] = sigma


    def ll(self, row):
        label, a = row['label'], row[self.name]
        average, sigma = self.params['average'], self.params['sigma']
        return super().ll(row) - math.log(sigma[label])-1/2*((a-average[label])/sigma[label])**2

class DiscreteColumn(Column):

    def parameters(self):
        super().parameters()
        p = {label:{a:0 for a in self.actions} for label in self.labels}
        count = self.params['count']
        for row in self.data.values():
            label,a = row['label'], row[self.name]
            p[label][a] += 1
        for label in self.labels:
            for a in self.actions:
                p[label][a] = p[label][a]/count[label]
        self.params['probability'] = p

    def ll(self, row):
        label, a = row['label'], row[self.name]
        p = self.params['probability']
        return super().ll(row) - math.log(p[label][a])

def legit_value(v):
    return (type(v) == str) or (type(v) in [float, int] and not math.isnan(v))

min_data = 20

#Load data
quizzes = []
students = {}
old_data_dir = config.main_dir + r"\Old data"
old_folders = [f for f in os.listdir(old_data_dir) if not os.path.isfile(os.path.join(old_data_dir, f))]
students = {}
columns = set()
types = {}
for folder in old_folders:
    data_dir = old_data_dir + "\\" + folder
    filename = os.path.join(data_dir, "Report.xlsx")
    dfstudents = pd.read_excel(filename, sheet_name = 'behavior') 
    dfstudents.fillna('missing', inplace=True)
    fstudents = dfstudents.to_dict(orient='index')
    
    for s in fstudents.values():
        names = s['Unnamed: 0'].split()
        name = names[1]+', '+names[0]+' '+names[3]
        students[name] = {a:s[a] for a in s if a != 'Unnamed: 0'}
        for a in s:
            if not a in columns:
                columns.add(a)
            if not a in types:
                types[a] = set()
            t = type(s[a])
            if (not s[a] in {'',0}) and legit_value(s[a]):
                types[a].add(t)
for column in types:
    if float in types[column]:
        types[column] = float
    else:
        types[column] = str

#Clean up data - drop columns that have less than 25% of answers
count = {column:0 for column in columns}
for student in students.values():
    for column in columns:
        if not column in student:
            student[column] = 'missing'
        if student[column] == 'missing': 
            student[column] = '' if types[column] == str else float('nan')
        v = student[column]
        t = type(v)
        if (t==str  or not math.isnan(v)):
            count[column] += 1
for column in columns:
    if count[column] < min_data:
        for student in students.values():
            del student[column]
columns = {column for column in columns if count[column] >= min_data}

values = {column:set(students[student][column] for student in students if not students[student][column] in ['', float('nan')]) for column in columns}

#Clean up data - other

#Assign first label
for student in students.values():
    student['label'] = str(student['Investment game I version #*']) + str(student['Stock Market Bubble #*']>50)

#Set up columns
dcolumns = []
for column in columns:
    if types[column] == str:
        dcolumns.append(DiscreteColumn(column, students))
    else: 
        dcolumns.append(GaussianColumn(column, students))
for dcolumn in dcolumns:
    dcolumn.parameters()

for dcolumn in dcolumns:
    k=3
#Save data
output_file = old_data_dir+r"\Behavior.xlsx"
writer = pd.ExcelWriter(output_file, engine="xlsxwriter")
reports = {'students':students, 'columns':{dc.name:dc.params for dc in dcolumns}}
for name in reports:
    data = dict(sorted(reports[name].items()))
    report = pd.DataFrame.from_dict(data).transpose()
    report.to_excel(writer, name)
writer.close()



