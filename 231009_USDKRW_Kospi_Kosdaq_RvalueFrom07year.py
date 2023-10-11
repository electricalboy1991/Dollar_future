import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# 데이터 전처리 함수
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

# 2007년 이후 데이터 필터링
filtered_data_2007 = merged_data[merged_data['Date'] >= '2007-01-01']
filtered_data_2007['Year'] = filtered_data_2007['Date'].dt.year

# 연도별 상관계수 계산
years = filtered_data_2007['Year'].unique()
correlations_kospi = [filtered_data_2007[filtered_data_2007['Year'] == year][['USD/KRW', 'KOSPI']].corr().iloc[0, 1] for year in years]
correlations_kosdaq = [filtered_data_2007[filtered_data_2007['Year'] == year][['USD/KRW', 'KOSDAQ']].corr().iloc[0, 1] for year in years]

# 평균 상관계수 계산
average_correlation_kospi = sum(correlations_kospi) / len(correlations_kospi)
average_correlation_kosdaq = sum(correlations_kosdaq) / len(correlations_kosdaq)

# 그래프 그리기
fig, ax = plt.subplots(1, 2, figsize=(14, 6))
palette = sns.color_palette("viridis", len(years))

# 산점도 그리기 및 상관계수, 회귀선 추가
for i, year in enumerate(years):
    year_data_kospi = filtered_data_2007[filtered_data_2007['Year'] == year]
    year_data_kosdaq = filtered_data_2007[filtered_data_2007['Year'] == year]

    # 산점도
    sns.scatterplot(x='USD/KRW', y='KOSPI', data=year_data_kospi, ax=ax[0], color=palette[i], s=10, label=f'{year}')
    sns.scatterplot(x='USD/KRW', y='KOSDAQ', data=year_data_kosdaq, ax=ax[1], color=palette[i], s=10, label=f'{year}')

    # 상관계수 표시
    ax[0].annotate(f'{year}: {correlations_kospi[i]:.2f}', (year_data_kospi['USD/KRW'].mean(), year_data_kospi['KOSPI'].mean()), color=palette[i], fontsize=8)
    ax[1].annotate(f'{year}: {correlations_kosdaq[i]:.2f}', (year_data_kosdaq['USD/KRW'].mean(), year_data_kosdaq['KOSDAQ'].mean()), color=palette[i], fontsize=8)

    # 회귀선
    m_kospi, b_kospi = np.polyfit(year_data_kospi['USD/KRW'], year_data_kospi['KOSPI'], 1)
    ax[0].plot(year_data_kospi['USD/KRW'], m_kospi * year_data_kospi['USD/KRW'] + b_kospi, color=palette[i], alpha=0.6)

    m_kosdaq, b_kosdaq = np.polyfit(year_data_kosdaq['USD/KRW'], year_data_kosdaq['KOSDAQ'], 1)
    ax[1].plot(year_data_kosdaq['USD/KRW'], m_kosdaq * year_data_kosdaq['USD/KRW'] + b_kosdaq, color=palette[i], alpha=0.6)

# 평균 상관계수 표시
ax[0].annotate(f'Avg Corr: {average_correlation_kospi:.2f}', xy=(0.05, 0.95), xycoords='axes fraction', fontsize=12, fontweight='bold', color='red')
ax[1].annotate(f'Avg Corr: {average_correlation_kosdaq:.2f}', xy=(0.05, 0.95), xycoords='axes fraction', fontsize=12, fontweight='bold', color='red')

# 타이틀 및 레이블
ax[0].set_title('USDKRW & KOSPI (2007~)')
ax[1].set_title('USDKRW & KOSDAQ (2007~)')

# 레전드 및 레이아웃 조정
ax[0].legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')
ax[1].legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

plt.show()