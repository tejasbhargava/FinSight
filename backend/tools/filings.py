from backend.rag.retriever import retrieve_chunks
from backend.utils.ticker_lookup import company_to_ticker
from langchain.tools import tool

def search_filings(
    company: str,
    question: str,
    chat_history: list = None
):
    """
    Search through a company's SEC 10-K annual filing for relevant excerpts.
    Use when question is about risks, strategy, competition, or fundamentals.
    Input should be company name and the specific question to search for.
    """
    if not question.strip():
        return []

    info = company_to_ticker(company)

    ticker = info["ticker"]

    return retrieve_chunks(
        ticker=ticker,
        question=question,
        chat_history=chat_history or []
    )

filings_tool = tool(search_filings)