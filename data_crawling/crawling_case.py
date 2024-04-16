import csv
import pandas as pd
import asyncio
import aiohttp
from lxml import html as lxml_html
from tqdm import tqdm
import nest_asyncio
import numpy as np

# 리스트를 초기화합니다
ID_list = []

# CSV 파일을 엽니다
with open('ID_list.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        ID_list.extend(row)


# asyncio 중첩 실행 가능하게 설정
nest_asyncio.apply()

base_url = "https://www.law.go.kr/LSW/precInfoP.do?precSeq="

# 각 열에 대한 빈 리스트 초기화
case_info = []
case_ids = []
case_details = []
judgment_summaries = []
referenced_statutes = []
referenced_precedents = []
attorneys = []
orders = []
reasons = []
judges = []

# ID와 세션을 받아 해당 URL의 텍스트를 반환하는 비동기 함수
async def fetch(ID, session):
    url = base_url + str(ID)
    async with session.get(url) as response:
        return await response.text()

# 메인 함수
async def main():
    async with aiohttp.ClientSession() as session:
        for i in tqdm(range(0, len(data), 80)):
            tasks = []
            for ID in data[i:i+80]:
                tasks.append(fetch(ID, session))
            htmls = await asyncio.gather(*tasks)
            for ID, html in zip(data[i:i+80], htmls):
                tree = lxml_html.fromstring(html)
                # 추출한 데이터를 각 리스트에 추가
                case_info.append(tree.xpath('//*[@id="contentBody"]/div[1]/text()'))
                case_ids.append(ID)
                case_details.append(tree.xpath('//*[@id="sa"]/following-sibling::p[@class="pty4"][1]//text()') if tree.xpath('//*[@id="sa"]') else np.nan)
                judgment_summaries.append(tree.xpath('//*[@id="yo"]/following-sibling::p[@class="pty4"][1]//text()') if tree.xpath('//*[@id="yo"]') else np.nan)
                referenced_statutes.append(tree.xpath('//*[@id="conLsJo"]/following-sibling::p[@class="pty4"][1]//text()') if tree.xpath('//*[@id="conLsJo"]') else np.nan)
                referenced_precedents.append(tree.xpath('//*[@id="conPrec"]/following-sibling::p[@class="pty4"][1]//text()') if tree.xpath('//*[@id="conPrec"]') else np.nan)
                orders.append(tree.xpath('//*[@id="conScroll"]/p[@class="pty4_dep1"][last()-1]/text()'))
                reasons.append(tree.xpath('//*[@id="conScroll"]/p[@class="pty4_dep1"][last()]/text()'))
                judges.append(tree.xpath('//*[@id="conScroll"]/div/text()') if tree.xpath('//*[@id="conScroll"]/div/text()') else np.nan)
                attorney_text = tree.xpath('//*[@id="conScroll"]/p[@class="pty4_dep1"][last()-3]/text()')
                keywords = ['변호사', '법무', '법인', '외']
                if attorney_text and any(keyword in ''.join(attorney_text) for keyword in keywords):
                    attorneys.append(attorney_text)
                else:
                    attorneys.append(np.nan)
            # 5초 대기
            await asyncio.sleep(5)

# 메인 함수 실행
asyncio.run(main())

# 리스트로부터 DataFrame 생성
df = pd.DataFrame({
    'Case Info' : case_info,
    'Case ID': case_ids,
    'Case Details': case_details,
    'Judgment Summary': judgment_summaries,
    'Referenced Statutes': referenced_statutes,
    'Referenced Precedents': referenced_precedents,
    'Attorney': attorneys,
    'Order': orders,
    'Reason': reasons,
    'Judge': judges
})
