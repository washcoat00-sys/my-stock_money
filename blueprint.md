
# Stock Analyzer

## Overview

A web-based tool to analyze stock performance over the last 3 years. Users can input a stock ticker symbol to get key performance indicators.

## Features

*   **Stock Ticker Input:** A simple input field for the user to enter the stock ticker.
*   **Performance Analysis:** The application calculates and displays the following metrics for the last 3 years of the selected stock:
    *   **CAGR (Compound Annual Growth Rate):** The mean annual growth rate of an investment over a specified period of time longer than one year.
    *   **Annualized Volatility:** A measure of how much the stock's returns fluctuate over a year.
    *   **Sharpe Ratio:** A measure of risk-adjusted return. It describes how much excess return you receive for the extra volatility you endure for holding a riskier asset.
    *   **MDD (Maximum Drawdown):** The maximum observed loss from a peak to a trough of a portfolio, before a new peak is attained.

## Design and Style

*   **Layout:** A clean, centered, single-card layout.
*   **Color Palette:** A simple and modern color palette with a blue primary color for interactive elements.
*   **Typography:** Clear and readable sans-serif font.
*   **User Experience:** An intuitive interface with a clear input field and a button to trigger the analysis. The results are displayed in a clean and easy-to-read format.

## Current Task

### Plan

1.  **Delete all existing files.** (Done)
2.  **Create `index.html`:** Set up the basic structure of the web page with an input field for the stock code and a button to trigger the analysis. (Done)
3.  **Create `style.css`:** Style the page with a clean and modern design. (Done)
4.  **Create `main.js`:**
    *   Add an event listener to the "Analyze" button.
    *   When the button is clicked, get the stock code from the input field.
    *   Fetch the last 3 years of stock data from the Yahoo Finance API.
    *   Calculate CAGR, Annualized Volatility, Sharpe Ratio, and MDD.
    *   Display the results on the page. (Done)
