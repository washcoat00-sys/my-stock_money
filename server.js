const express = require('express');
const cors = require('cors');
const YahooFinance = require('yahoo-finance2').default;

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());

const yf = new YahooFinance({ suppressNotices: ['ripHistorical'] });

app.get('/api/stock/:ticker', async (req, res) => {
    const { ticker } = req.params;
    
    // Using period1 and period2 for 3 years
    const d = new Date();
    const period2 = d.toISOString().split('T')[0]; // today
    d.setFullYear(d.getFullYear() - 3);
    const period1 = d.toISOString().split('T')[0]; // 3 years ago
    
    const queryOptions = {
        period1: period1,
        period2: period2,
        interval: '1d'
    };

    try {
        const result = await yf.chart(ticker, queryOptions);
        
        // Map the new chart response to what our frontend expects
        if (!result || !result.quotes || result.quotes.length === 0) {
            return res.status(404).json({ error: 'No data found' });
        }

        const prices = result.quotes.map(quote => quote.close).filter(p => p != null);
        
        res.json({
            ticker: ticker,
            prices: prices,
            currency: result.meta.currency,
            symbol: result.meta.symbol
        });

    } catch (error) {
        console.error('Error fetching data:', error.message);
        res.status(500).json({ error: 'Error fetching data from Yahoo Finance', details: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
