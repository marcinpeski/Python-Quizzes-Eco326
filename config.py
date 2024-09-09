import os

session = "2024S"

#main_dir = r"C:\Users\Marcin\OneDrive - University of Toronto\Documents\A My work\A teaching\ECO326\Python Quizzes Eco326"
main_dir = os.getcwd()
data_dir = main_dir+r"\DataECO326_"+session
quizz_directory = data_dir + r"\Quizz Reports"
due_dates_file = data_dir + r"\DueDates.xlsx"
output_file = data_dir + r"\Report.xlsx"
#Compare file was a document prepared by TA Mahmood Haddara - that I wanted to double check to compare the results.  
compare_file = data_dir + r"\NewQuizGrades.xlsx"

old_data_directory = data_dir + r"\Old data"