import pandas as pd
import requests
from lxml import html as lxml_html
import re
import csv

# requests.get 날릴 base_rul
# base_url = f"http://www.law.go.kr/DRF/lawSearch.do?target=prec&OC=hsk9174&type=HTML&display=100&page={}&org=400201&JO=형법"

# 판례 ID받아올 리스트
ID_list = []

# ID가 담긴 하이퍼링크 받아오는 코드 (총 75페이지)

for page in range(1,75):
    url = f"http://www.law.go.kr/DRF/lawSearch.do?target=prec&OC=hsk9174&type=HTML&display=100&page={page}&org=400201&JO=형법"
    response = requests.get(url)

    # html로 받았으므로, html로 파싱
    tree = lxml_html.fromstring(response.content)

    # XPath 주소로 하이퍼링크 주소에 접근하기
    addresses = tree.xpath("/html/body/form/div/table/tbody/tr/td/a/@href")

    # 해당 주소가 ID_number라는 리스트로 담김. 
    # 해당 리스트 요소에서 정규표현식을 통해 숫자 제외 전부 제외
    for address in addresses:
        match = re.search(r'ID=(\d+)', address)
        ID = match.group(1)
        ID_list.append(ID)

# 생성된 ID_list에 관하여 CSV파일로 바로 저장
with open('ID_list.csv', 'w', newline ='') as file:
    writer = csv.writer(file)
    writer.writerow(ID_list)