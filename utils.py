import pandas as pd
import numpy as np
import yfinance as yf

RISK_FREE = 0.065          # Indian 10Y G-Sec, approximate
TRADING_DAYS = 252


def load_portfolio(path="portfolio.csv"):
    df = pd.read_csv(path)
    df["Weight"] = df["Weight"] / df["Weight"].sum()
    return df


def fetch_prices(tickers, period="2y"):
    data = yf.download(tickers, period=period, auto_adjust=True)["Close"]
    return data.dropna()


def compute_returns(prices):
    return prices.pct_change().dropna()


def portfolio_series(returns, portfolio):
    """Weight individual asset returns into a single portfolio return series."""
    weights = portfolio.set_index("Ticker")["Weight"]
    weights = weights.reindex(returns.columns)   # align with price column order
    return (returns * weights).sum(axis=1)


def metrics(port_returns):
    ann_return = (1 + port_returns.mean()) ** TRADING_DAYS - 1
    ann_vol = port_returns.std() * np.sqrt(TRADING_DAYS)
    sharpe = (ann_return - RISK_FREE) / ann_vol
    cumulative = (1 + port_returns).cumprod()
    drawdown = (cumulative / cumulative.cummax() - 1).min()
    return {
        "annual_return": ann_return,
        "annual_volatility": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": drawdown,
    }
def correlation_matrix(returns):
    return returns.corr()


def concentration(portfolio):
    """Herfindahl index — 1/N for equal weights, 1.0 for a single holding."""
    w = portfolio["Weight"]
    return (w ** 2).sum()
def risk_score(m, portfolio):
    """Transparent heuristic — not an industry-standard risk model."""
    score = 0
    breakdown = {}

    vol = m["annual_volatility"]
    pts = 40 if vol < 0.15 else 25 if vol < 0.22 else 10
    breakdown["Volatility"] = pts
    score += pts

    pts = 30 if m["sharpe"] > 1 else 20 if m["sharpe"] > 0 else 5
    breakdown["Risk-adjusted return"] = pts
    score += pts

    max_w = portfolio["Weight"].max()
    pts = 20 if max_w < 0.35 else 10 if max_w < 0.50 else 0
    breakdown["Concentration"] = pts
    score += pts

    n = len(portfolio)
    pts = 10 if n >= 5 else 5 if n >= 3 else 0
    breakdown["Holdings count"] = pts
    score += pts

    label = "Low risk" if score >= 75 else "Moderate risk" if score >= 50 else "High risk"
    return score, label, breakdown