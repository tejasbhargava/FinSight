import yfinance as yf
from backend.utils.ticker_lookup import company_to_ticker
from langchain.tools import tool

def get_stock_data(company: str) -> dict:
    """
    Get live stock price, PE ratio, market cap, revenue, earnings,
    dividend yield and other financial metrics for a company.
    Use when the question is about valuation, price, or financial performance.
    Input should be company name like 'Apple' or 'Microsoft'.
    """
    info = company_to_ticker(company)
    ticker = info["ticker"]

    stock = yf.Ticker(ticker)
    data = stock.info
    if not data:
        raise ValueError(
            f"Could not fetch stock data for {ticker}"
        )
    return {
        "ticker": ticker,
        "company_name": data.get("longName") or info["company_name"],
        "price": data.get("currentPrice") or data.get("regularMarketPrice"),
        "currency": data.get("currency"),
        "market_cap": data.get("marketCap"),
        "pe_ratio": data.get("trailingPE"),
        "forward_pe": data.get("forwardPE"),
        "eps": data.get("trailingEps"),
        "52_week_high": data.get("fiftyTwoWeekHigh"),
        "52_week_low": data.get("fiftyTwoWeekLow"),
        "volume": data.get("volume"),
        "avg_volume": data.get("averageVolume"),
        "dividend_yield": data.get("dividendYield"),
        "revenue": data.get("totalRevenue"),
        "net_income": data.get("netIncomeToCommon"),
        "debt_to_equity": data.get("debtToEquity"),
        "return_on_equity": data.get("returnOnEquity"),
        "sector": data.get("sector"),
        "industry": data.get("industry"),
        "summary": data.get("longBusinessSummary", "")[:500],
    }

stock_tool = tool(get_stock_data)