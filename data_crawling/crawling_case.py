import csv

# 리스트를 초기화합니다
ID_list = []

# CSV 파일을 엽니다
with open('ID_list.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        ID_list.extend(row)

