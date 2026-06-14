import yfinance as yf

def company_to_ticker(company: str) -> dict:
    company = company.strip()

    search = yf.Search(company, max_results=1)
    quotes = search.quotes

    if not quotes:
        raise ValueError(f"Could not find ticker for '{company}'")

    quote = quotes[0]

    ticker = quote.get("symbol")

    if not ticker:
        raise ValueError(f"No symbol found for '{company}'")

    return {
        "ticker": ticker.upper(),
        "company_name": (
            quote.get("shortname")
            or quote.get("longname")
            or company
        )
    }

if __name__ == "__main__":
    result = company_to_ticker("microsoft")
    print(result)