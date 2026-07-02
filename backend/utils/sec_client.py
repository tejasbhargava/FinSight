import requests
import os
from backend.config import settings

HEADERS = {"User-Agent": "finsight tejasbhargava9@gmail.com"}  # SEC requires this

def get_company_cik(ticker: str) -> str:
    response = requests.get(
        "https://www.sec.gov/files/company_tickers.json",
        headers=HEADERS
    )
    response.raise_for_status()
    
    data = response.json()
    
    for entry in data.values():
        if entry["ticker"].upper() == ticker.upper():
            cik = str(entry["cik_str"]).zfill(10)  # SEC needs 10-digit CIK
            return cik
    
    raise ValueError(f"CIK not found for ticker: {ticker}")


def get_latest_filing_url(cik: str, form_type: str = "10-K") -> str:
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    data = response.json()
    filings = data["filings"]["recent"]
    
    forms = filings["form"]
    accession_numbers = filings["accessionNumber"]
    primary_documents = filings["primaryDocument"]
    
    for i, form in enumerate(forms):
        if form == form_type:
            accession = accession_numbers[i].replace("-", "")
            doc = primary_documents[i]
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{doc}"
            return filing_url
    
    raise ValueError(f"No {form_type} found for CIK: {cik}")


def download_latest_filing(ticker: str, form_type: str = "10-K") -> str:
    cik = get_company_cik(ticker)
    filing_url = get_latest_filing_url(cik, form_type)
    
    response = requests.get(filing_url, headers=HEADERS)
    response.raise_for_status()
    
    # save to data/filings/TICKER/
    save_dir = os.path.join(settings.FILINGS_PATH, ticker.upper())
    os.makedirs(save_dir, exist_ok=True)
    
    ext = "html" if filing_url.endswith(".htm") or filing_url.endswith(".html") else "txt"
    save_path = os.path.join(save_dir, f"{form_type}.{ext}")
    
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    return save_path

def main():

    path = download_latest_filing(
        ticker="NVDA",
        form_type="10-K"
    )

    print(path)

if __name__ == "__main__":
    main()