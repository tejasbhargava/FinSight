import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rag.retriever import retrieve_chunks

# ---------------------------
# EVAL DATASET
# manually curated — question + which section the answer SHOULD come from
# ---------------------------
EVAL_SET = [

    # ---------------- APPLE (Consumer Tech) ----------------
    {
        "ticker": "AAPL",
        "question": "How does Apple generate most of its revenue?",
        "expected_section": "Item 1"
    },
    {
        "ticker": "AAPL",
        "question": "What are Apple's biggest supply chain and manufacturing risks?",
        "expected_section": "Item 1A"
    },
    {
        "ticker": "AAPL",
        "question": "How does Apple management explain recent financial performance?",
        "expected_section": "Item 7"
    },
    {
        "ticker": "AAPL",
        "question": "What competitive challenges could affect Apple's long-term growth?",
        "expected_section": "Item 1A"
    },

    # ---------------- MICROSOFT (Enterprise Software) ----------------
    {
        "ticker": "MSFT",
        "question": "How does Microsoft describe its cloud and Azure business?",
        "expected_section": "Item 1"
    },
    {
        "ticker": "MSFT",
        "question": "What cybersecurity and regulatory risks does Microsoft disclose?",
        "expected_section": "Item 1A"
    },
    {
        "ticker": "MSFT",
        "question": "How does management discuss Microsoft's revenue and operating income?",
        "expected_section": "Item 7"
    },
    {
        "ticker": "MSFT",
        "question": "What growth opportunities does Microsoft highlight for its business?",
        "expected_section": "Item 1"
    },

    # ---------------- NVIDIA (Semiconductors) ----------------
    {
        "ticker": "NVDA",
        "question": "How does Nvidia describe its AI and data center business?",
        "expected_section": "Item 1"
    },
    {
        "ticker": "NVDA",
        "question": "What export control and geopolitical risks does Nvidia face?",
        "expected_section": "Item 1A"
    },
    {
        "ticker": "NVDA",
        "question": "How does Nvidia management explain its recent revenue growth?",
        "expected_section": "Item 7"
    },
    {
        "ticker": "NVDA",
        "question": "What competitive risks could impact Nvidia's AI leadership?",
        "expected_section": "Item 1A"
    },

    # ---------------- JPMORGAN (Banking) ----------------
    {
        "ticker": "JPM",
        "question": "How does JPMorgan generate revenue across its major business segments?",
        "expected_section": "Item 1"
    },
    {
        "ticker": "JPM",
        "question": "What credit and macroeconomic risks does JPMorgan disclose?",
        "expected_section": "Item 1A"
    },
    {
        "ticker": "JPM",
        "question": "How does management discuss JPMorgan's recent financial performance?",
        "expected_section": "Item 7"
    },
    {
        "ticker": "JPM",
        "question": "What interest rate risks could affect JPMorgan's business?",
        "expected_section": "Item 1A"
    },

    # ---------------- COSTCO (Retail) ----------------
    {
        "ticker": "COST",
        "question": "How does Costco's membership model contribute to its business?",
        "expected_section": "Item 1"
    },
    {
        "ticker": "COST",
        "question": "What supply chain and inventory risks does Costco disclose?",
        "expected_section": "Item 1A"
    },
    {
        "ticker": "COST",
        "question": "How does management explain Costco's sales growth and profitability?",
        "expected_section": "Item 7"
    },
    {
        "ticker": "COST",
        "question": "What competitive advantages does Costco highlight in its retail business?",
        "expected_section": "Item 1"
    },
]

# ---------------------------
# EVAL RUNNER
# ---------------------------
def run_eval():
    total = len(EVAL_SET)
    hits = 0
    misses = []

    print(f"\nRunning retrieval eval on {total} questions...\n")
    print("=" * 70)

    for i, item in enumerate(EVAL_SET, start=1):
        ticker = item["ticker"]
        question = item["question"]
        expected = item["expected_section"].lower().strip()

        try:
            chunks = retrieve_chunks(ticker=ticker, question=question)

            # check if expected section appears in ANY of the retrieved chunks
            retrieved_sections = [
                c.get("section", "").lower().strip()
                for c in chunks
            ]

            # more robust matching
            hit = any(
                expected.replace(" ", "").replace(".", "") in 
                section.replace(" ", "").replace(".", "")
                for section in retrieved_sections
            )

            status = "✅ HIT " if hit else "❌ MISS"
            print(f"[{i:02d}] {status} | {ticker} | {question[:50]}...")
            print(f"       Expected: {item['expected_section']}")
            print(f"       Retrieved: {[c.get('section') for c in chunks]}")
            print()

            if hit:
                hits += 1
            else:
                misses.append(item)

        except Exception as e:
            print(f"[{i:02d}] ⚠️  ERROR | {ticker} | {str(e)}\n")
            total -= 1   # don't count errored questions in denominator

    hit_rate = (hits / total) * 100 if total > 0 else 0

    print("=" * 70)
    print(f"\n📊 RESULTS")
    print(f"Total Questions : {total}")
    print(f"Hits            : {hits}")
    print(f"Misses          : {total - hits}")
    print(f"Hit Rate        : {hit_rate:.1f}%")

    if misses:
        print(f"\n❌ MISSED QUESTIONS:")
        for m in misses:
            print(f"  - [{m['ticker']}] {m['question']}")

    print("\n")
    return hit_rate


if __name__ == "__main__":
    hit_rate = run_eval()