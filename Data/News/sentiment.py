# 라이브러리 불러오기
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

# VADER 초기화
vader_analyzer = SentimentIntensityAnalyzer()

# FinBERT 초기화
finbert = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")

# CSV 파일 불러오기
# '파일경로.csv'를 업로드한 CSV 파일 경로로 교체하세요.
file_path = 'VADER_FinBERT_TEST_Panasonic.csv'
data = pd.read_csv(file_path)

# 데이터프레임 컬럼 확인
print("컬럼 목록:", data.columns)

# '전처리' 열에 텍스트 데이터가 있다고 가정
# 필요한 경우, '전처리' 대신 텍스트가 포함된 열 이름으로 바꾸세요.
text_column = '전처리'

# 분석 결과를 저장할 리스트
sentiment_scores = []
sentiment_labels = []


# 감성 분석 수행
for text in data[text_column]:
    # VADER 분석
    vader_score = vader_analyzer.polarity_scores(text)
    vader_compound = round(vader_score['compound'], 2)  # 소수점 둘째 자리까지 반올림

    # FinBERT 분석
    finbert_result = finbert(text)[0]
    finbert_label = finbert_result['label']

    # 중립적이거나 명확한 어조를 가진 경우 VADER 또는 FinBERT를 신뢰하는 로직
    if abs(vader_compound) <= 0.05:
        # 중립적이면 FinBERT 사용
        final_label = finbert_label
    else:
        # 명확한 어조이면 VADER 사용
        if vader_compound > 0.05:
            final_label = "Positive"
        elif vader_compound < -0.05:
            final_label = "Negative"


    # 결과 저장
    sentiment_scores.append(vader_compound)
    sentiment_labels.append(final_label)


# 결과를 데이터프레임에 추가
data['감성점수'] = sentiment_scores
data['감성결과'] = sentiment_labels


# 결과 미리보기
print(data.head())

# 결과를 CSV로 저장
output_file_path = '감성분석_결과.csv'
data.to_csv(output_file_path, index=False, encoding='utf-8-sig')

print(f"감성 분석 결과가 '{output_file_path}'에 저장되었습니다.")
