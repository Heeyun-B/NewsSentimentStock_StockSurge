import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re

def parse_date(date_str, crawl_start_time):
    """날짜 문자열을 파싱하여 datetime 객체로 변환합니다."""
    # 상대적인 날짜 처리
    match = re.match(r'(\d+)(시간|일) 전', date_str)
    if match:
        num = int(match.group(1))  # 숫자 추출
        unit = match.group(2)  # 단위 추출
        if unit == "시간":
            return crawl_start_time - timedelta(hours=num)
        elif unit == "일":
            return crawl_start_time - timedelta(days=num)
    # 절대적인 날짜 처리
    date_formats = ["%Y.%m.%d.", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y"]
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return pd.NaT  # 처리할 수 없는 형식

def crawl_news(query, start_date, end_date, max_pages=10):
    """네이버 뉴스를 크롤링합니다."""
    news_list = []
    crawl_start_time = datetime.now()  # 크롤링 시작 시간 고정

    for page in range(1, max_pages + 1):
        start = (page - 1) * 10 + 1
        # 제공된 URL을 사용하되, query 부분만 동적으로 변경
        url = f"https://search.naver.com/search.naver?where=news&query={query}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={start_date}&de={end_date}&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Afrom{start_date.replace('.', '')}to{end_date.replace('.', '')}&is_sug_officeid=0&office_category=0&service_area=0&start={start}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('div.news_area')

        for article in articles:
            title = article.select_one('a.news_tit').get_text()
            link = article.select_one('a.news_tit')['href']
            summary = article.select_one('div.dsc_wrap').get_text()
            date_str = article.select_one('.info_group span.info').get_text()

            # 날짜 파싱
            parsed_date = parse_date(date_str, crawl_start_time)

            # 유효한 날짜만 추가
            if pd.notna(parsed_date):
                news_list.append({
                    'keyword': query,  # 키워드 추가
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'date': parsed_date
                })

    # 데이터프레임 변환 및 중복 제거
    news_df = pd.DataFrame(news_list)
    news_df = news_df.drop_duplicates(subset=["title", "link"])

    # 데이터 확인: date 열이 없으면 기본값 추가
    if 'date' not in news_df.columns:
        news_df['date'] = pd.NaT

    return news_df

# 뉴스 크롤링 실행
query = "lg energy solution"
start_date = "2024.12.01"  # 시작 날짜 (YYYY.MM.DD 형식)
end_date = "2024.12.25"    # 종료 날짜 (YYYY.MM.DD 형식)
max_pages = 200             # 최대 크롤링 페이지 수

news_df = crawl_news(query, start_date, end_date, max_pages)

# 날짜 기준으로 오름차순 정렬
news_df = news_df.sort_values(by='date', ascending=True).reset_index(drop=True)

# 결과 출력
print(news_df)

# CSV 파일로 저장
news_df.to_csv('lg_energy_solution_뉴스기사_241201_241225.csv', index=False, encoding='utf-8-sig')
