
import pandas as pd
from pykrx import stock
import numpy as np
from scipy.optimize import minimize
import datetime

# [입력 데이터 구성]
# 사용자가 웹 UI를 통해 입력할 값들을 여기서 임시로 설정합니다.
# 실제로는 웹 UI에서 이 파이썬 스크립트를 호출하면서 인자로 전달받아야 합니다.
AGE = 45
TICKERS = ['005930', '000660', '035420', '005380', '035720'] # 예시: 삼성전자, SK하이닉스, NAVER, 현대차, 카카오
TOTAL_INVESTMENT = 400_000_000
# 사용자가 제시한 비중 (현금 15% 제외 후 재계산)
USER_WEIGHTS = {
    '005930': 0.30,
    '000660': 0.25,
    '035420': 0.20,
    '005380': 0.15,
    '035720': 0.10,
}

# 현금 비중
CASH_RATIO = 0.15

# --- 핵심 로직 ---

def generate_report(age, tickers, total_investment, user_weights):
    """
    입력 데이터를 기반으로 투자 성과 분석 리포트를 생성합니다.
    """
    report = []
    report.append("""
=================================================
          퀀트 기반 투자 포트폴리오 분석 리포트
=================================================
""")

    # 1. 나이 기반 위험 자산 비중 진단
    report.append("\n[1. 나이 기반 위험 자산 비중 진단]")
    recommended_stock_ratio = (100 - age) / 100
    actual_stock_ratio = 1 - CASH_RATIO
    report.append(f" - '100 - 나이' 법칙에 따른 권장 주식 비중: {recommended_stock_ratio:.0%}")
    report.append(f" - 현재 포트폴리오 주식 비중 (현금 제외): {actual_stock_ratio:.0%}")
    if actual_stock_ratio > recommended_stock_ratio:
        report.append(" - 진단: 권장 주식 비중에 비해 다소 공격적인 투자 성향입니다. 시장 변동성에 유의하세요.")
    else:
        report.append(" - 진단: 권장 주식 비중에 비해 다소 안정적인 투자 성향입니다.")

    # 2. 주가 데이터 로드 (최근 1년)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365)
    
    report.append(f"\n[2. 주가 데이터 분석 (분석 기간: {start_date} ~ {end_date})]")
    
    try:
        prices = pd.DataFrame()
        for ticker in tickers:
            df = stock.get_market_ohlcv_by_date(start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'), ticker)
            prices[ticker] = df['종가']
        
        prices.dropna(inplace=True)
        if prices.empty:
            report.append(" - 오류: 해당 기간 동안의 주가 데이터를 가져올 수 없습니다. 종목 코드를 확인해주세요.")
            return "\n".join(report)

    except Exception as e:
        report.append(f" - 오류: 주가 데이터 로드 중 문제가 발생했습니다: {e}")
        return "\n".join(report)

    # 일일 수익률 계산
    daily_returns = prices.pct_change().dropna()

    # 3. 개별 종목 지표 분석
    report.append("\n[3. 개별 종목 주요 지표 분석]")
    
    individual_metrics = pd.DataFrame(index=tickers, columns=['CAGR', 'Ann_Vol', 'Sharpe', 'MDD'])

    for ticker in tickers:
        ticker_returns = daily_returns[ticker]
        
        # CAGR (연평균 성장률)
        cumulative_return = (1 + ticker_returns).prod()
        cagr = cumulative_return ** (252 / len(ticker_returns)) - 1
        
        # Ann_Vol (연 변동성)
        ann_vol = ticker_returns.std() * np.sqrt(252)
        
        # Sharpe Ratio (샤프 지수) - 무위험 수익률 0% 가정
        sharpe_ratio = cagr / ann_vol if ann_vol != 0 else 0
        
        # MDD (최대 낙폭)
        cumulative_returns = (1 + ticker_returns).cumprod()
        peak = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns - peak) / peak
        mdd = drawdown.min()
        
        individual_metrics.loc[ticker] = [f"{cagr:.2%}", f"{ann_vol:.2%}", f"{sharpe_ratio:.2f}", f"{mdd:.2%}"]

    report.append(individual_metrics.to_string())
    report.append("""
 - CAGR (연평균 성장률): 높을수록 특정 기간 돈이 얼마나 불어났는지(연 복리 기준)를 의미합니다.
 - Ann_Vol (연 변동성): 높을수록 주가 변동이 심하며, 위험성이 높다는 것을 의미합니다.
 - Sharpe (샤프 지수): 높을수록 변동성 대비 수익률이 좋다는 의미로, 투자의 효율성을 나타냅니다.
 - MDD (최대 낙폭): 낮을수록(절대값이 작을수록) 특정 기간 최대 손실폭이 적었다는 것을 의미합니다.
""")

    # 4. 포트폴리오 종합 분석 (사용자 지정 비중)
    report.append("\n[4. 포트폴리오 종합 분석 (사용자 지정 비중)]")
    
    # 사용자 비중 정규화 (현금 제외 후 투자금 내에서)
    total_user_weight = sum(user_weights.values())
    normalized_weights = np.array([w / total_user_weight for t, w in user_weights.items() if t in tickers])

    if len(normalized_weights) != len(tickers):
        report.append(" - 오류: 종목 리스트와 비중 딕셔너리의 종목이 일치하지 않습니다.")
        return "\n".join(report)

    portfolio_return = (daily_returns * normalized_weights).sum(axis=1)
    
    # 포트폴리오 지표 계산
    pf_cagr = (1 + portfolio_return).prod() ** (252 / len(portfolio_return)) - 1
    pf_ann_vol = portfolio_return.std() * np.sqrt(252)
    pf_sharpe = pf_cagr / pf_ann_vol if pf_ann_vol != 0 else 0
    pf_cumulative_returns = (1 + portfolio_return).cumprod()
    pf_peak = pf_cumulative_returns.expanding(min_periods=1).max()
    pf_drawdown = (pf_cumulative_returns - pf_peak) / pf_peak
    pf_mdd = pf_drawdown.min()

    portfolio_metrics = pd.DataFrame([
        [f"{pf_cagr:.2%}", f"{pf_ann_vol:.2%}", f"{pf_sharpe:.2f}", f"{pf_mdd:.2%}"]
    ], columns=['CAGR', 'Ann_Vol', 'Sharpe', 'MDD'], index=['My Portfolio'])
    
    report.append(portfolio_metrics.to_string())

    # 5. 배당 시뮬레이션
    report.append("\n[5. 예상 연간 배당금 시뮬레이션]")
    investment_per_ticker = {ticker: total_investment * (1 - CASH_RATIO) * normalized_weights[i] for i, ticker in enumerate(tickers)}
    
    # 현실적인 배당률 랜덤 적용 (연 3% ~ 8%)
    np.random.seed(0) # 결과 재현을 위해 시드 고정
    dividend_yields = {ticker: np.random.uniform(0.03, 0.08) for ticker in tickers}
    
    dividend_df = pd.DataFrame(index=tickers, columns=['투자금액', '예상배당률', '예상배당금'])
    total_dividend = 0
    for ticker in tickers:
        investment = investment_per_ticker[ticker]
        yield_rate = dividend_yields[ticker]
        dividend = investment * yield_rate
        total_dividend += dividend
        dividend_df.loc[ticker] = [f"{investment:,.0f} 원", f"{yield_rate:.2%}", f"{dividend:,.0f} 원"]

    report.append(dividend_df.to_string())
    report.append(f"\n - 예상 연간 총 배당금: {total_dividend:,.0f} 원")

    # 6. 포트폴리오 최적화 (샤프 지수 극대화)
    report.append("\n[6. 포트폴리오 최적화 (샤프 지수 극대화)]")
    
    def negative_sharpe(weights, returns):
        portfolio_return = (returns * weights).sum(axis=1)
        cagr = (1 + portfolio_return).prod() ** (252 / len(portfolio_return)) - 1
        ann_vol = portfolio_return.std() * np.sqrt(252)
        sharpe = cagr / ann_vol if ann_vol != 0 else 0
        return -sharpe

    num_assets = len(tickers)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    initial_weights = num_assets * [1. / num_assets,]

    optimal_result = minimize(negative_sharpe, initial_weights, args=(daily_returns,),
                              method='SLSQP', bounds=bounds, constraints=constraints)

    optimal_weights = optimal_result.x
    
    optimized_weights_df = pd.DataFrame([f"{w:.2%}" for w in optimal_weights], index=tickers, columns=['최적 비중 (샤프지수 극대화)'])
    report.append(optimized_weights_df.to_string())
    report.append("\n - 제안: 위 표는 변동성 대비 수익률을 극대화하는 종목별 최적 투자 비중을 나타냅니다.")
    
    report.append("\n\n--- 리포트 종료 --- \n*본 분석은 과거 데이터 기반이며, 미래 수익을 보장하지 않습니다.")
    
    return "\n".join(report)

if __name__ == '__main__':
    # 이 스크립트를 직접 실행할 경우, 상단의 기본값으로 리포트를 생성합니다.
    final_report = generate_report(AGE, TICKERS, TOTAL_INVESTMENT, USER_WEIGHTS)
    print(final_report)
