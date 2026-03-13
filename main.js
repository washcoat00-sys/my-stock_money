
document.addEventListener("DOMContentLoaded", function() {
    const analyzeButton = document.getElementById("analyze-button");
    const stockInput = document.getElementById("stock-input");
    const resultsDiv = document.getElementById("results");

    analyzeButton.addEventListener("click", async function() {
        const stockCode = stockInput.value.toUpperCase();
        if (!stockCode) {
            resultsDiv.innerHTML = "<p>Please enter a stock code.</p>";
            return;
        }

        resultsDiv.innerHTML = "<p>Analyzing...</p>";

        try {
            const response = await fetch(`https://query1.finance.yahoo.com/v7/finance/download/${stockCode}?period1=${Math.floor(Date.now() / 1000) - 94608000}&period2=${Math.floor(Date.now() / 1000)}&interval=1d&events=history`);
            if (!response.ok) {
                throw new Error("Failed to fetch stock data. Please check the stock code.");
            }
            const data = await response.text();
            
            // Basic data parsing and calculations in JavaScript
            const rows = data.split('\n').slice(1);
            const prices = rows.map(row => {
                const columns = row.split(',');
                return parseFloat(columns[4]); // Adj Close
            }).filter(price => !isNaN(price));

            if (prices.length < 2) {
                throw new Error("Not enough data to perform analysis.");
            }

            const cagr = calculateCAGR(prices);
            const annVol = calculateAnnVol(prices);
            const sharp = calculateSharpeRatio(cagr, annVol);
            const mdd = calculateMDD(prices);

            resultsDiv.innerHTML = `
                <h3>${stockCode} Analysis (3 Years)</h3>
                <p>CAGR: ${cagr.toFixed(2)}%</p>
                <p>Annualized Volatility: ${annVol.toFixed(2)}%</p>
                <p>Sharpe Ratio: ${sharp.toFixed(2)}</p>
                <p>Maximum Drawdown (MDD): ${mdd.toFixed(2)}%</p>
            `;

        } catch (error) {
            resultsDiv.innerHTML = `<p>Error: ${error.message}</p>`;
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
