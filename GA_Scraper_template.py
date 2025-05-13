import requests
from bs4 import BeautifulSoup
import csv
import time

# === Configuration ===
BASE_URL = "https://www.ilga.gov/legislation/witnessslip.asp"
GA_PARAMS = {
    "DocTypeID": "HB",           # Document type (e.g., HB, SB)
    "GA": "YOUR_GA_HERE",        # General Assembly number (e.g., 102)
    "GAID": "YOUR_GAID_HERE",    # Internal session ID
    "SessionID": "YOUR_SESSION_ID_HERE",
    "SpecSess": ""
}
OUTPUT_FILE = "witness_slips_output.csv"
START_BILL = 1
END_BILL = 100  # Set to the last HB number to scrape

# === HTML Parsing ===
def extract_counts(soup):
    td_elements = soup.find_all("td", class_="tabcontrol")
    if not td_elements or len(td_elements) < 3:
        return 0, 0, 0
    def extract(text): return int(text.split(":")[1].strip()) if ":" in text else 0
    return extract(td_elements[0].text), extract(td_elements[1].text), extract(td_elements[2].text)

# === Scraper Logic ===
def get_witness_data(doc_num):
    params = GA_PARAMS.copy()
    params["DocNum"] = str(doc_num)
    url = f"{BASE_URL}?DocNum={doc_num}&DocTypeID={params['DocTypeID']}&LegID=&GAID={params['GAID']}&SessionID={params['SessionID']}&GA={params['GA']}&SpecSess="

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        prop, opp, nopos = extract_counts(soup)

        return {
            "bill_number": f"{params['DocTypeID']}{doc_num:04d}",
            "title": "",
            "doc_num": doc_num,
            "proponents": prop,
            "opponents": opp,
            "no_position": nopos,
            "total_slips": prop + opp + nopos,
            "witness_slip_url": url
        }

    except Exception as e:
        print(f"Error on {params['DocTypeID']}{doc_num:04d}: {e}")
        return None

# === Scraping Loop ===
results = []
for doc_num in range(START_BILL, END_BILL + 1):
    print(f"Scraping {GA_PARAMS['DocTypeID']}{doc_num:04d}...")
    row = get_witness_data(doc_num)
    if row:
        results.append(row)
    time.sleep(0.1)

# === Output ===
if results:
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"Done. Data saved to {OUTPUT_FILE}")
else:
    print("No data scraped.")
