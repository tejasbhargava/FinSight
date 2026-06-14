from backend.llm import generate_response
from backend.tools.stock import get_stock_data
from backend.tools.news import get_company_news
from backend.tools.filings import search_filings
import json


SYSTEM_PROMPT = """
You are FinSight, an expert AI financial research assistant.

You will be given structured data from multiple sources:
- Stock data: live market data, valuation metrics
- News: recent headlines and developments
- SEC Filings: official 10-K annual report excerpts

Your job is to synthesize all provided data into a clear, grounded, and insightful answer.

Rules:
- Always ground your answer in the provided data
- When relevant, mention whether information comes from stock data,
recent news, or SEC filings.
- Be concise but thorough
- If data is missing or unavailable, say so
- Never hallucinate financial figures
"""


def run_query(
    company: str,
    question: str,
    chat_history: list = None
) -> dict:
    chat_history = chat_history or []

    # gather all contexts in parallel — no routing
    context = {}

    try:
        context["stock"] = get_stock_data(company)
    except Exception as e:
        context["stock"] = {"error": str(e)}

    try:
        context["news"] = get_company_news(company)
        context["news"] = context["news"][:3]
    except Exception as e:
        context["news"] = {"error": str(e)}

    try:
        context["filings"] = search_filings(
            company=company,
            question=question,
            chat_history=chat_history
        )
        context["filings"] = context["filings"][:5]
    except Exception as e:
        context["filings"] = {"error": str(e)}

    context_str = json.dumps(context, indent=2, default=str)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *chat_history,
        {
            "role": "user",
            "content": f"""
Company: {company}
Question: {question}

Data:
{context_str}

Answer the question using the data above.
"""
        }
    ]

    answer = generate_response(messages)
    tools_used = []

    if "error" not in context["stock"]:
        tools_used.append("stock")

    if "error" not in context["news"]:
        tools_used.append("news")

    if "error" not in context["filings"]:
        tools_used.append("filings")

    return {
        "answer": answer,
        "tools_used": tools_used,
        "sources": ["stock data", "news", "sec filings"]
    } 

def main():

    result = run_query(
        company="Apple",
        question="What are Apple's biggest business risks?"
    )

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(result["answer"])

    print("\n" + "=" * 80)
    print("TOOLS USED")
    print("=" * 80)

    print(result["tools_used"])

    print("\n" + "=" * 80)
    print("SOURCES")
    print("=" * 80)

    print(result["sources"])


if __name__ == "__main__":
    main()