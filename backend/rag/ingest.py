import os
import re

from bs4 import BeautifulSoup

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from backend.config import settings
from backend.utils.sec_client import download_latest_filing


def extract_text_from_filing(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if file_path.endswith((".html", ".htm")):

        soup = BeautifulSoup(content, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

    else:
        text = content

    return text


def extract_sections(text: str) -> list[dict]:
    """
    SEC filings usually contain:

    Item 1.
    Item 1A.
    Item 1B.
    Item 7.
    Item 7A.
    Item 8.

    We split on these section headers.
    """

    pattern = r"(Item\s+\d+[A-Z]?\.)"

    parts = re.split(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    sections = []

    for i in range(1, len(parts), 2):

        title = parts[i].strip()

        if i + 1 >= len(parts):
            continue

        content = parts[i + 1].strip()

        if len(content) < 100:
            continue

        sections.append(
            {
                "title": title,
                "content": content
            }
        )

    return sections


def build_documents(
    text: str,
    ticker: str,
    form_type: str
) -> list[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " "
        ]
    )

    documents = []

    sections = extract_sections(text)

    # fallback if section extraction fails
    if not sections:

        chunks = splitter.split_text(text)

        for chunk in chunks:

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "ticker": ticker,
                        "form_type": form_type,
                        "section": "Unknown"
                    }
                )
            )

        return documents

    for section in sections:

        section_name = section["title"]

        chunks = splitter.split_text(
            section["content"]
        )

        for chunk in chunks:

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "ticker": ticker,
                        "form_type": form_type,
                        "section": section_name
                    }
                )
            )

    return documents


def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5"
    )


def ingest_filing(
    ticker: str,
    form_type: str = "10-K"
) -> int:

    print(f"\nDownloading {form_type} for {ticker}...")

    file_path = download_latest_filing(
        ticker=ticker,
        form_type=form_type
    )

    print("Extracting text...")

    text = extract_text_from_filing(
        file_path
    )

    print("Building documents...")

    documents = build_documents(
        text=text,
        ticker=ticker,
        form_type=form_type
    )

    print(
        f"Total chunks created: {len(documents)}"
    )

    print(
        "Generating embeddings and creating FAISS index..."
    )

    embeddings = get_embeddings()

    vectorstore = FAISS.from_documents(
        documents,
        embeddings
    )

    index_dir = os.path.join(
        settings.INDEXES_PATH,
        ticker.upper()
    )

    os.makedirs(
        index_dir,
        exist_ok=True
    )

    vectorstore.save_local(index_dir)

    print(
        f"FAISS index saved to: {index_dir}"
    )

    return len(documents)


def main():

    total_chunks = ingest_filing(
        ticker="COST",
        form_type="10-K"
    )

    print(
        f"\nSuccessfully indexed {total_chunks} chunks."
    )


if __name__ == "__main__":
    main()