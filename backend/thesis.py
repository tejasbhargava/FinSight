from backend.llm import generate_response

from backend.tools.stock import get_stock_data
from backend.tools.news import get_company_news
from backend.tools.filings import search_filings

import json


THESIS_SYSTEM_PROMPT = """
You are FinSight, an expert AI financial research assistant.

You are generating a professional investment research report.

Data sources available:

1. Stock market data
2. Recent news
3. SEC filings

Rules:

- Ground every statement in the provided data
- Never invent financial figures
- Clearly separate facts from interpretation
- Use SEC filings as the primary source for business quality and risks
- Use news only for recent developments
- Use stock metrics for valuation and financial analysis
- Do not provide direct buy/sell recommendations
- Be objective and balanced
"""


def gather_company_context(
    company: str,
    chat_history: list = None
) -> dict:

    context = {}

    try:

        context["stock"] = get_stock_data(
            company
        )

    except Exception as e:

        context["stock"] = {
            "error": str(e)
        }

    try:

        news = get_company_news(
            company
        )

        # keep prompt size manageable
        context["news"] = news[:5]

    except Exception as e:

        context["news"] = {
            "error": str(e)
        }

    try:

        filings = search_filings(
            company=company,
            question="""
            Business overview,
            competitive advantages,
            growth opportunities,
            risks,
            strategy,
            long-term outlook
            """,
            chat_history=chat_history or []
        )

        # top chunks only
        context["filings"] = filings[:8]

    except Exception as e:

        context["filings"] = {
            "error": str(e)
        }

    return context


def build_tools_used(
    context: dict
) -> list:

    tools_used = []

    if (
        isinstance(context.get("stock"), dict)
        and "error" not in context["stock"]
    ):
        tools_used.append(
            "stock"
        )

    if not (
        isinstance(context.get("news"), dict)
        and "error" in context["news"]
    ):
        tools_used.append(
            "news"
        )

    if not (
        isinstance(context.get("filings"), dict)
        and "error" in context["filings"]
    ):
        tools_used.append(
            "filings"
        )

    return tools_used


def generate_investment_thesis(
    company: str,
    chat_history: list = None
) -> dict:

    chat_history = chat_history or []

    print(
        f"Building thesis for {company}..."
    )

    context = gather_company_context(
        company,
        chat_history
    )

    context_str = json.dumps(
        context,
        indent=2,
        default=str
    )

    messages = [
        {
            "role": "system",
            "content": THESIS_SYSTEM_PROMPT
        },

        *chat_history,

        {
            "role": "user",
            "content": f"""
Generate a professional investment research report for:

{company}

Data:

{context_str}

Use the following structure.

# Executive Summary

Provide a concise summary of the company,
its strengths,
risks,
and overall business quality.

# Business Overview

Explain:

- What the company does
- Core products and services
- Revenue drivers

# Competitive Advantages

Discuss:

- Moats
- Brand strength
- Network effects
- Cost advantages
- Switching costs

# Growth Drivers

Discuss:

- New products
- New markets
- Industry tailwinds
- Expansion opportunities

# Financial Snapshot

Analyze:

- Revenue
- Profitability
- Market Cap
- PE Ratio
- Debt Levels
- Return Metrics

# Recent Developments

Summarize key news.

# Bull Case

Provide the strongest arguments supporting long-term success.

# Bear Case

Provide the strongest arguments against long-term success.

# Key Risks

Use SEC filings heavily.

Discuss:

- Competitive risks
- Regulatory risks
- Operational risks
- Macroeconomic risks

# Long-Term Outlook

Provide a balanced assessment.

# Conclusion

Summarize the overall investment thesis.

Do NOT provide investment advice.

Do NOT say buy or sell.
"""
        }
    ]

    report = generate_response(
        messages
    )

    return {
        "company": company,
        "report": report,
        "tools_used": build_tools_used(
            context
        ),
        "sources": [
            "stock",
            "news",
            "sec_filings"
        ]
    }


def main():

    result = generate_investment_thesis(
        company="Apple"
    )

    print("\n")
    print("=" * 100)
    print("INVESTMENT THESIS")
    print("=" * 100)

    print(
        result["report"]
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