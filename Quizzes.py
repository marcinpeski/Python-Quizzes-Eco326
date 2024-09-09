from config import *
import QuizzClasses
import os
import pandas as pd
from datetime import timedelta, datetime

def read_due_dates(quizzes):
    due_dates = pd.read_excel(due_dates_file)
    for row in due_dates.itertuples():
        name = getattr(row,'Name').replace(u'\xa0', u' ')
        for quizz in quizzes:
            if quizz.is_name(name):
                date = getattr(row,'Date').to_pydatetime()
                time_zone = getattr(row,'Timezone')
                date += timedelta(hours = 23, minutes = 59)
                if time_zone == 'EST':
                    date += timedelta(hours = 5)
                else:
                    date += timedelta(hours = 4)
                quizz.set_due_date(date)

#Factory method to create quizzes
def create_quizz(filename):
    if 'Investment Game I version'.lower() in filename.lower(): return QuizzClasses.InvestmentGameI(filename)
    if 'Investment Game II version'.lower() in filename.lower(): return QuizzClasses.InvestmentGameII(filename)
    if 'Duel'.lower() in filename.lower(): return QuizzClasses.Duel(filename)
    if 'Schelling'.lower() in filename.lower(): return QuizzClasses.Schelling(filename)
    if 'Bertrand duopoly'.lower() in filename.lower(): return QuizzClasses.BertrandDuopoly(filename)
    if 'Hotelling'.lower() in filename.lower(): return QuizzClasses.Hotelling(filename)
    if 'Grab the dollar'.lower() in filename.lower(): return QuizzClasses.GrabDollar(filename)
    if 'Battle of Sexes with Incomplete Information'.lower() in filename.lower(): return QuizzClasses.BattleSexesIncomplete(filename)
    if 'Finitely Repeated'.lower() in filename.lower(): return QuizzClasses.FinitelyRepeated(filename)
    if 'Stag hunt'.lower() in filename.lower(): return QuizzClasses.StagHunt(filename)
    if 'Stock Market'.lower() in filename.lower(): 
        if 'II version'.lower() in filename.lower(): return QuizzClasses.StockMarketII(filename)
        else: return QuizzClasses.StockMarket(filename)
    #if 'First price'.lower() in filename.lower(): return QuizzClasses.FirstPriceAuction(filename)
    if 'Movie and Battle'.lower() in filename.lower(): return QuizzClasses.MovieBattleSexes(filename)
    if 'Ultimatum'.lower() in filename.lower(): return QuizzClasses.Ultimatum(filename)
    if 'Raffle'.lower() in filename.lower(): return QuizzClasses.Raffle(filename)
    if 'Two jars'.lower() in filename.lower(): return QuizzClasses.TwoJars(filename)
    if 'First-price auction'.lower() in filename.lower(): return QuizzClasses.FirstPriceAuction(filename)
    if 'Traffic game'.lower() in filename.lower(): return QuizzClasses.TrafficGame(filename)
    return None

#load quizzes and students
def load_quizzes(data_dir = data_dir, quizz_directory=quizz_directory):
    quizzes = []
    students = {}
    filenames = [f for f in os.listdir(quizz_directory) if os.path.isfile(os.path.join(quizz_directory, f))]
    for filename in filenames:
        if filename.split(".")[1] == "csv":
            quizz = create_quizz(filename)
            if quizz != None:
                print('LOAD: ',quizz)
                quizz.load()
                quizzes.append(quizz)
    read_due_dates(quizzes)
    for quizz in quizzes:
        quizz.read_students(students,quizzes)
    for quizz in quizzes:
        print('ANALYZE: ',quizz)
        quizz.analyze()
    quizzes.sort(key = lambda x: x.due_date)
    return quizzes, students

#save Quizz scores
def save_grades():
    filenames = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    for filename in filenames:
        if filename.split(".")[1] == "csv" and "Grades" in filename.split(".")[0]:
            grades_file_with_path = os.path.join(data_dir, filename)

    print('READING STUDENT GRADES AND SAVING THEIR SCORES')
    grades_file = pd.read_csv(grades_file_with_path)
    participation_column, id_column, midterm_column, final_column, score_column = None, None, None, None, None
    for column in grades_file.columns:
        if isinstance(column, str) and 'Participation' in column: participation_column = column
        if isinstance(column, str) and 'SIS User ID' in column: id_column = column
        if isinstance(column, str) and 'Midterm (' in column: midterm_column = column
        if isinstance(column, str) and 'Make up' in column: makeup_column = column
        if isinstance(column, str) and 'Final exam' in column: final_column = column
        if isinstance(column, str) and 'Quiz Score' in column: score_column = column
    grades_file.set_index(id_column)
    for s in students:
        student = students[s]
        for index, row in grades_file.iterrows():
            if row[id_column] == student.id:
                if midterm_column != None and not pd.isna(row[midterm_column]): student.midterm = round(float(row[midterm_column]))
                if makeup_column != None and not pd.isna(row[makeup_column]): student.midterm = round(float(row[makeup_column]))
                if final_column != None and not pd.isna(row[final_column]): student.final = round(float(row[final_column]))

    for quizz in quizzes:
        quiz_column = None
        for column in grades_file.columns:
            if isinstance(column, str) and quizz.name in column: quiz_column = column
        for student in quizz.students.values():
            if student.id in grades_file[id_column].values:
                grades_file.loc[grades_file[id_column] == student.id, quiz_column] = student.quizzes[quizz.name]['payoff']
    for student in students.values():
        participation = 0
        for q in student.quizzes.values():
            if q['participate'] == 1 and q['on time']: participation += 1 
        grades_file.loc[grades_file[id_column] == student.id, participation_column] = participation
        grades_file.loc[grades_file[id_column] == student.id, score_column] = student.total_score()
    grades_file.to_csv(grades_file_with_path, index=False)

def prepare_report():
    #prepare Report
    writer = pd.ExcelWriter(output_file, engine="xlsxwriter")
    report = pd.DataFrame.from_records([])
    report.to_excel(writer,'Summary')
    l=0
    worksheet = writer.sheets['Summary']
    quizzes.sort(key=lambda x: x.due_date, reverse=True)
    for quizz in quizzes:
        head = quizz.head_info()
        for line in head:
            i = 0
            for item in line:
                worksheet.write(l,i,item)
                i += 1
            l += 1
        l += 1
    report = pd.DataFrame.from_records([students[s].to_report() for s in students])
    report.to_excel(writer,'All students')

    report = pd.DataFrame.from_records([students[s].to_report_scores() for s in students])
    report.to_excel(writer,'All scores')

    behavior = {}
    for student in students.values():
        id = student.name+' # '+str(student.index)
        behavior[id] = {}
        for quiz in student.quizzes.values():
            if 'strategy' in quiz:
                s = quiz['strategy']
                for a in s:
                    behavior[id][quiz['quizz'].name+"#"+str(a)] = s[a]
    report = pd.DataFrame(behavior).transpose()
    report.to_excel(writer, "behavior")

    for quizz in quizzes:
        print('REPORT: ',quizz)
        head = quizz.head_info()
        nlines = len(head)
        report = pd.DataFrame.from_records([students[s].report(quizz) for s in students])
        report.to_excel(writer,quizz.name, startrow = nlines+1, startcol = 0)
        worksheet = writer.sheets[quizz.name]
        l = 0
        for line in head:
            i = 0
            for item in line:
                worksheet.write(l,i,item)
                i += 1
            l += 1

    writer.close()


quizzes, students = load_quizzes()
save_grades()
prepare_report()