
document.addEventListener("DOMContentLoaded", function() {
    const analyzeButton = document.getElementById("analyze-button");
    const stockInput = document.getElementById("stock-input");
    const resultsDiv = document.getElementById("results");

    analyzeButton.addEventListener("click", async function() {
        const stockCode = stockInput.value.toUpperCase().trim();
        if (!stockCode) {
            resultsDiv.innerHTML = "<p>종목 코드를 입력해주세요.</p>";
            return;
        }

        resultsDiv.innerHTML = "<p>분석 중...</p>";

        let queryCode = stockCode;
        if (/^\d{6}$/.test(stockCode)) {
            queryCode = stockCode + '.KS'; // KOSPI 기본
        }

                try {

                    // Use our local proxy server to avoid CORS/Rate Limit issues

                    let response = await fetch(`http://localhost:3000/api/stock/${queryCode}`);

                    

                    if (!response.ok && /^\d{6}$/.test(stockCode)) {

                        // KOSPI가 아니면 KOSDAQ 시도

                        queryCode = stockCode + '.KQ';

                        response = await fetch(`http://localhost:3000/api/stock/${queryCode}`);

                    }

        

                    if (!response.ok) {

                        throw new Error("주가 데이터를 가져오는데 실패했습니다. 올바른 한국 주식 종목 코드인지 확인해 주세요.");

                    }

                    

                    const data = await response.json();

                    

                    if (!data.prices || data.prices.length < 2) {

                        throw new Error("분석을 수행하기에 데이터가 충분하지 않습니다.");

                    }

        

                    const prices = data.prices;

                    const cagr = calculateCAGR(prices);
            const annVol = calculateAnnVol(prices);
            const sharp = calculateSharpeRatio(cagr, annVol);
            const mdd = calculateMDD(prices);

            resultsDiv.innerHTML = `
                <h3>${stockCode} 분석 결과 (최근 3년)</h3>
                <p>CAGR (연평균 성장률): ${cagr.toFixed(2)}%</p>
                <p>연간 변동성: ${annVol.toFixed(2)}%</p>
                <p>샤프 지수: ${sharp.toFixed(2)}</p>
                <p>최대 낙폭 (MDD): ${mdd.toFixed(2)}%</p>
            `;

        } catch (error) {
            resultsDiv.innerHTML = `<p>오류: ${error.message}</p>`;
        }
    });

    function calculateCAGR(prices) {
        const startPrice = prices[0];
        const endPrice = prices[prices.length - 1];
        return (Math.pow(endPrice / startPrice, 1 / 3) - 1) * 100;
    }

    function calculateAnnVol(prices) {
        const dailyReturns = [];
        for (let i = 1; i < prices.length; i++) {
            dailyReturns.push((prices[i] / prices[i - 1]) - 1);
        }
        const stdDev = Math.sqrt(dailyReturns.reduce((acc, val) => acc + Math.pow(val - (dailyReturns.reduce((a, b) => a + b) / dailyReturns.length), 2), 0) / (dailyReturns.length - 1));
        return stdDev * Math.sqrt(252) * 100;
    }

    function calculateSharpeRatio(cagr, annVol) {
        const riskFreeRate = 0.02; // Assuming a 2% risk-free rate
        return (cagr / 100 - riskFreeRate) / (annVol / 100);
    }

    function calculateMDD(prices) {
        let peak = -Infinity;
        let maxDrawdown = 0;
        for (const price of prices) {
            if (price > peak) {
                peak = price;
            }
            const drawdown = (peak - price) / peak;
            if (drawdown > maxDrawdown) {
                maxDrawdown = drawdown;
            }
        }
        return maxDrawdown * 100;
    }
});
