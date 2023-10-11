import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import mplcursors


# 데이터 전처리 함수 정의
def preprocess_data(df, value_column):
    df['날짜'] = pd.to_datetime(df['날짜'].str.strip(), format='%Y- %m- %d')
    df[value_column] = df[value_column].str.replace(',', '').astype(float)
    return df[['날짜', value_column]]


# 데이터 로드
kospi_data = pd.read_csv('코스피지수 과거 데이터.csv')
kosdaq_data = pd.read_csv('코스닥 과거 데이터.csv')
usd_krw_data = pd.read_csv('USD_KRW 과거 데이터.csv')

# 데이터 전처리
kospi_clean = preprocess_data(kospi_data, '종가')
kosdaq_clean = preprocess_data(kosdaq_data, '종가')
usd_krw_clean = preprocess_data(usd_krw_data, '종가')

# 데이터 병합
merged_data = pd.merge(kospi_clean, kosdaq_clean, on='날짜', how='inner', suffixes=('_kospi', '_kosdaq'))
merged_data = pd.merge(merged_data, usd_krw_clean, on='날짜', how='inner')
merged_data.columns = ['Date', 'KOSPI', 'KOSDAQ', 'USD/KRW']

# 2023년도 데이터 필터링 및 월 정보 추가
data_2023 = merged_data[(merged_data['Date'] >= '2023-01-01') & (merged_data['Date'] < '2024-01-01')].copy()
data_2023['Month'] = data_2023['Date'].dt.strftime('%b')


# 월별 색상 팔레트 설정
months = data_2023['Month'].unique()
palette = sns.color_palette("viridis", len(months))

# 월별 상관계수 계산 및 추세선 그리기
correlations_kospi = []
correlations_kosdaq = []

fig, ax = plt.subplots(1, 2, figsize=(14, 6))

# 월별로 산점도 그리기, 상관계수 계산 및 추세선 그리기
for i, month in enumerate(months):
    month_data_kospi = data_2023[data_2023['Month'] == month]
    month_data_kosdaq = data_2023[data_2023['Month'] == month]

    # 산점도
    sns.scatterplot(x='USD/KRW', y='KOSPI', data=month_data_kospi, ax=ax[0], color=palette[i], s=10, label=f'{month}')
    sns.scatterplot(x='USD/KRW', y='KOSDAQ', data=month_data_kosdaq, ax=ax[1], color=palette[i], s=10, label=f'{month}')

    # 회귀선
    m_kospi, b_kospi = np.polyfit(month_data_kospi['USD/KRW'], month_data_kospi['KOSPI'], 1)
    ax[0].plot(month_data_kospi['USD/KRW'], m_kospi * month_data_kospi['USD/KRW'] + b_kospi, color=palette[i], alpha=0.6)

    m_kosdaq, b_kosdaq = np.polyfit(month_data_kosdaq['USD/KRW'], month_data_kosdaq['KOSDAQ'], 1)
    ax[1].plot(month_data_kosdaq['USD/KRW'], m_kosdaq * month_data_kosdaq['USD/KRW'] + b_kosdaq, color=palette[i], alpha=0.6)

    # 상관계수 계산 및 저장
    corr_kospi = month_data_kospi[['USD/KRW', 'KOSPI']].corr().iloc[0, 1]
    corr_kosdaq = month_data_kosdaq[['USD/KRW', 'KOSDAQ']].corr().iloc[0, 1]
    correlations_kospi.append(corr_kospi)
    correlations_kosdaq.append(corr_kosdaq)

    # 상관계수 표시
    ax[0].annotate(f'{corr_kospi:.2f}',
                   (month_data_kospi['USD/KRW'].mean(), m_kospi * month_data_kospi['USD/KRW'].mean() + b_kospi),
                   textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8, color=palette[i])
    ax[1].annotate(f'{corr_kosdaq:.2f}',
                   (month_data_kosdaq['USD/KRW'].mean(), m_kosdaq * month_data_kosdaq['USD/KRW'].mean() + b_kosdaq),
                   textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8, color=palette[i])

# 월별 상관계수의 평균 계산
average_corr_kospi = np.mean(correlations_kospi)
average_corr_kosdaq = np.mean(correlations_kosdaq)

# 평균 상관계수 표시
ax[0].annotate(f'Avg Corr: {average_corr_kospi:.2f}', xy=(0.05, 0.95), xycoords='axes fraction', fontsize=12, fontweight='bold', color='red')
ax[1].annotate(f'Avg Corr: {average_corr_kosdaq:.2f}', xy=(0.05, 0.95), xycoords='axes fraction', fontsize=12, fontweight='bold', color='red')

# 타이틀 및 레이블
ax[0].set_title('USDKRW & KOSPI (2023)')
ax[1].set_title('USDKRW & KOSDAQ (2023)')

# 레전드 및 레이아웃 조정
ax[0].legend(title='Month', bbox_to_anchor=(1.05, 1), loc='upper left')
ax[1].legend(title='Month', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
# 툴팁 활성화
mplcursors.cursor(ax[0].scatter(data_2023['USD/KRW'], data_2023['KOSPI'], c=data_2023['Month'].astype('category').cat.codes, cmap='viridis', s=10), hover=True).connect(
    "add", lambda sel: sel.annotation.set_text(data_2023['Date'].iloc[sel.target.index].strftime('%Y-%m-%d'))
)

mplcursors.cursor(ax[1].scatter(data_2023['USD/KRW'], data_2023['KOSDAQ'], c=data_2023['Month'].astype('category').cat.codes, cmap='viridis', s=10), hover=True).connect(
    "add", lambda sel: sel.annotation.set_text(data_2023['Date'].iloc[sel.target.index].strftime('%Y-%m-%d'))
)

plt.show()
