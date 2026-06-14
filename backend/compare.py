from backend.llm import generate_response
from backend.tools.stock import get_stock_data
from backend.tools.news import get_company_news
from backend.tools.filings import search_filings

import json


COMPARE_SYSTEM_PROMPT = """
You are FinSight, an expert AI financial research assistant.

You are comparing two public companies using:

1. Stock market data
2. Recent news
3. SEC filings

Rules:

- Ground every claim in the provided data
- Never invent financial figures
- Mention when information is unavailable
- Compare companies side-by-side
- Be balanced and objective
- Prefer SEC filing evidence over news opinions
- Focus on business fundamentals, risks, profitability, growth and valuation
"""


def get_company_profile(
    company: str,
    question: str,
    chat_history: list = None
) -> dict:

    profile = {}

    # ------------------------
    # STOCK
    # ------------------------

    try:

        stock = get_stock_data(company)

        profile["stock"] = stock

    except Exception as e:

        profile["stock"] = {
            "error": str(e)
        }

    # ------------------------
    # NEWS
    # ------------------------

    try:

        news = get_company_news(company)

        # keep prompt small
        profile["news"] = news[:3]

    except Exception as e:

        profile["news"] = {
            "error": str(e)
        }

    # ------------------------
    # FILINGS
    # ------------------------

    try:

        filings = search_filings(
            company=company,
            question=question,
            chat_history=chat_history or []
        )

        # top retrieved chunks only
        profile["filings"] = filings[:5]

    except Exception as e:

        profile["filings"] = {
            "error": str(e)
        }

    return profile


def build_tools_used(
    profile1: dict,
    profile2: dict
):

    tools_used = set()

    for profile in [profile1, profile2]:

        if (
            isinstance(profile.get("stock"), dict)
            and "error" not in profile["stock"]
        ):
            tools_used.add("stock")

        if not (
            isinstance(profile.get("news"), dict)
            and "error" in profile["news"]
        ):
            tools_used.add("news")

        if not (
            isinstance(profile.get("filings"), dict)
            and "error" in profile["filings"]
        ):
            tools_used.add("filings")

    return list(tools_used)


def run_compare(
    company1: str,
    company2: str,
    question: str,
    chat_history: list = None
) -> dict:

    chat_history = chat_history or []

    print(f"Fetching profile for {company1}...")

    profile1 = get_company_profile(
        company1,
        question,
        chat_history
    )

    print(f"Fetching profile for {company2}...")

    profile2 = get_company_profile(
        company2,
        question,
        chat_history
    )

    context = {
        company1: profile1,
        company2: profile2
    }

    context_str = json.dumps(
        context,
        indent=2,
        default=str
    )

    messages = [
        {
            "role": "system",
            "content": COMPARE_SYSTEM_PROMPT
        },

        *chat_history,

        {
            "role": "user",
            "content": f"""
Compare {company1} and {company2}.

User Question:
{question}

Data:
{context_str}

Create a structured report using the following sections:

# Financial Snapshot
- Revenue
- Net Income
- Market Cap
- PE Ratio
- Debt Levels
- Profitability

# Recent Developments
- Important recent events
- Product launches
- Regulatory developments

# Business & Competitive Position
- Competitive advantages
- Growth opportunities
- Industry position

# Key Risks
- Risks from SEC filings
- Operational risks
- Regulatory risks

# Side-by-Side Comparison Table

# Overall Assessment
- Relative strengths
- Relative weaknesses
- Situations where each company may outperform the other

Do NOT provide investment advice.
"""
        }
    ]

    answer = generate_response(
        messages
    )

    tools_used = build_tools_used(
        profile1,
        profile2
    )

    return {
        "comparison": answer,
        "tools_used": tools_used,
        "sources": [
            company1,
            company2
        ]
    }


def main():

    result = run_compare(
        company1="Apple",
        company2="Microsoft",
        question="Compare their long-term business risks and growth opportunities."
    )

    print("\n")
    print("=" * 100)
    print("COMPARISON")
    print("=" * 100)

    print(
        result["comparison"]
    )

    print("\n")
    print("=" * 100)
    print("TOOLS USED")
    print("=" * 100)

    print(
        result["tools_used"]
    )


if __name__ == "__main__":
    main()