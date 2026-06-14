import requests
from backend.utils.ticker_lookup import company_to_ticker
from backend.config import settings
from langchain.tools import tool


def get_company_news(company: str) -> list[dict]:
    """
    Get recent news headlines and developments about a company.
    Use when question is about recent events, sentiment, launches, or lawsuits.
    Input should be company name like 'Apple' or 'Microsoft'.
    """
    info = company_to_ticker(company)
    company_name = info["company_name"]
    ticker = info["ticker"]

    url = "https://newsdata.io/api/1/news"
    params = {
        "q": ticker,
        "apikey": settings.NEWS_API_KEY,
        "language": "en",
    }

    response = requests.get(url, params=params)
    print(response.status_code)
    print(response.text)
    response.raise_for_status()

    articles = response.json().get("articles", [])

    return [
        {
            "title": a.get("title"),
            "source": a.get("source", {}).get("name"),
            "published_at": a.get("publishedAt"),
            "description": a.get("description"),
            "url": a.get("url"),
        }
        for a in articles[:3]
    ]

news_tool = tool(get_company_news)
def main():

    news = get_company_news(
        "Apple"
    )

    for article in news:

        print(
            article["title"]
        )

        print(
            article["source"]
        )

        print("-" * 50)


if __name__ == "__main__":
    main()