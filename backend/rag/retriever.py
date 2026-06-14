from backend.llm import generate_response
from backend.config import settings
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def contextualize_question(
    question: str,
    chat_history: list,
):
    if not chat_history:
        return question

    rewrite_prompt = f"""
Given the chat history and the latest user question,
formulate a standalone question that can be understood
without the chat history.

Do NOT answer the question.
Only rewrite it if needed.

Chat History:
{chat_history}

Current Question:
{question}

Standalone Question:
"""

    standalone_question = generate_response(
        [
            {
                "role": "user",
                "content": rewrite_prompt
            }
        ]
    )

    return standalone_question.strip()


def load_vectorstore(ticker: str):

    index_dir = os.path.join(
        settings.INDEXES_PATH,
        ticker.upper()
    )

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5"
    )

    vectorstore = FAISS.load_local(
        index_dir,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore


def retrieve_chunks(
    ticker: str,
    question: str,
    chat_history: list = None
):

    standalone_question = contextualize_question(
        question,
        chat_history
    )

    vectorstore = load_vectorstore(ticker)

    results = vectorstore.max_marginal_relevance_search(
        standalone_question,
        k=settings.TOP_K,
        fetch_k=20
    )

    return [
        {
            "content": doc.page_content,
            "section": doc.metadata.get("section"),
            "source": doc.metadata.get("form_type")
        }
        for doc in results
    ]

def main():

    docs = retrieve_chunks(
        ticker="AAPL",
        question="What are Apple's biggest risks?",
        chat_history=[]
    )

    print("\nRetrieved Documents\n")
    print("=" * 80)

    for i, doc in enumerate(docs, start=1):

        print(f"\nDocument {i}")

        print(
            f"Section: {doc.get('section')}"
        )

        print(
            f"Source: {doc.get('source')}"
        )

        print("\nContent Preview:")

        print(
            doc["content"][:500]
        )

        print("\n" + "=" * 80)


if __name__ == "__main__":
    main()