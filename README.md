# Illinois General Assembly Witness Slip Scraper

## Project Goal  
Scrape accurate witness slip data (proponents, opponents, no position) for all Illinois House Bills across multiple General Assembly (GA) sessions and optionally enrich that data using LegiScan bill metadata.

---

## Key Components Required

### 1. ILGA Website Access
- Witness slip URL structure:  
  `https://www.ilga.gov/legislation/witnessslip.asp?...`
- Bill status URL structure used for `DocNum`, `GA`, etc.

### 2. Correct Session Identifiers
Each GA session uses:
- `GA` (General Assembly number)
- `GAID` (internal session ID)
- `SessionID`

Each ILGA bill page is constructed using a combination of:
- `GA` (General Assembly number)
- `GAID` (internal session identifier)
- `SessionID` (session instance)
- `DocNum` (bill number)

These parameters are visible in the URL and must match the session metadata for a bill. 

Here’s a visual reference showing how these parameters appear:

![ILGA URL Structure](https://github.com/jakec04/ILGA_scraper/blob/50bc6ed14b5d775d53bfe46085fc51c9f2115a22/URL_structure.png)

### 3. HTML Structure
Witness slip counts are found inside:
```html
<td class="tabcontrol">Proponents: X</td>
```

### 4. JSON Metadata (from LegiScan)
LegiScan exports per-bill metadata:
- `bill_number`, `title`, `sponsors`, `status`, etc.
- Used to determine bill counts per GA and enrich outputs

### 5. Output Structure
CSV with:
```
bill_number, title, doc_num, proponents, opponents, no_position, total_slips, witness_slip_url
```

---

## Iterative Process Summary

### 1. Base Scraper for 103rd GA (HB1–4000)
- Built Python script using `requests` + `BeautifulSoup`
- Initially parsed full witness slip tables (inaccurate)

### 2. Switched to Summary Counts
- Validated HTML shows totals inside `.tabcontrol` cells
- New parsing logic:
```python
td_elements = soup.find_all("td", class_="tabcontrol")
proponents = extract(td_elements[0].text)
```

### 3. Tested with Small Sample
- Limited scrape to HB1–25 to verify data

### 4. Fixed “0 Remaining Bills” Bug
- Caused by using an incomplete CSV for doc_num comparisons
- Fix:
```python
df['doc_num'] = pd.to_numeric(df['doc_num'], errors='coerce')
```

### 5. Scraped Remaining Bills
- Used range skipping existing bills
- Example:
```python
range(4001, 5924)
```
- Added 0.1s delay and progress printout

### 6. Incorporated LegiScan JSON Metadata
Used to:
- Count number of actual House Bills
- Validate or enrich scraped witness slip data

Steps:
```python
len([f for f in os.listdir(json_dir) if f.startswith('HB')])
```
- Merging based on `bill_number` or extracted `doc_num`

```

---

## Dependencies

```bash
pip install requests beautifulsoup4 pandas
```

---

## Directory Requirements

- Folder of LegiScan JSONs (e.g., `path/to/JSON/folder`)
- Output CSVs: `103rd_HB_SLIPS.csv`, `102nd_HB_SLIPS.csv`, etc.

---

## Optional Features (For Future Development)

- Auto-resume or fail-safe logic
- Merge with JSON metadata inline
- Write error logs
- Save to SQLite, JSONL, or upload to GitHub



---

## Data Analysis Guide

Once you have your `*.csv` output file, you can run statistical summaries to understand witness slip patterns across bills.

### Example: Summarize `total_slips` Column

Create a script named `summarize_slip_statistics.py` with the following:

```python
import pandas as pd

# Load your CSV
df = pd.read_csv("103rd_HB_SLIPS.csv")  # or your file path

# Descriptive stats
print("Descriptive Statistics for total_slips:")
print(df["total_slips"].describe())

# Additional insights
print("\nBills with 0 slips:", (df["total_slips"] == 0).sum())
print("Bills with > 100 slips:", (df["total_slips"] > 100).sum())
print("Bills with > 500 slips:", (df["total_slips"] > 500).sum())
print("Bills with > 1000 slips:", (df["total_slips"] > 1000).sum())

# Top 10 bills by slip volume
print("\nTop 10 bills by total_slips:")
print(df.sort_values("total_slips", ascending=False)[["bill_number", "total_slips"]].head(10))
```

### Optionally Save Results to a File

```python
with open("slip_summary.txt", "w") as f:
    f.write(df["total_slips"].describe().to_string())
    f.write(f"\n\nBills with 0 slips: {(df['total_slips'] == 0).sum()}")
    f.write(f"\nBills with > 100 slips: {(df['total_slips'] > 100).sum()}")
    f.write(f"\nBills with > 500 slips: {(df['total_slips'] > 500).sum()}")
    f.write(f"\nBills with > 1000 slips: {(df['total_slips'] > 1000).sum()}")
```

---

This analysis helps reveal how many bills received large volumes of public input, and can identify the most contentious or widely supported legislation in each session.

---

## Scraper Template and Example Usage

To make the scraper reusable across sessions and bill types, use the following template:

### `witness_slip_scraper_template.py`

```python
# Replace 'YOUR_GA_HERE', 'YOUR_GAID_HERE', and 'YOUR_SESSION_ID_HERE' with real session values
# Set START_BILL and END_BILL to define the range
# Output goes to 'witness_slips_output.csv'

# (See full script in repository: witness_slip_scraper_template.py)
```

Download the script:  
[witness_slip_scraper_template.py](witness_slip_scraper_template.py)

---

## Example Export File

A sample CSV output from running the scraper on the 103rd General Assembly can be found here:  
[Export_example.csv](https://github.com/jakec04/ILGA_scraper/blob/40ff0e72c08f30654142822a559359e0f9432692/Export_example.csv)

It contains:
- `bill_number`
- `doc_num`
- `proponents`, `opponents`, `no_position`
- `total_slips`, `witness_slip_url`

---

## Where to Find LegiScan JSON Files

To obtain JSON bill exports from LegiScan for enrichment or bill list reference, use this interface:

![Where to Get LegiScan JSON Files](https://github.com/jakec04/ILGA_scraper/blob/40ff0e72c08f30654142822a559359e0f9432692/LegiScan_Help.png)

---

This guide, script template, and example outputs are meant to streamline both the data scraping and analysis phases of tracking public legislative input in Illinois.
---

## Attribution

Created and maintained by [Jake Cox](https://github.com/jakec04)  

*Legislative Datasets by LegiScan LLC is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)*

Built with guidance and troubleshooting support from OpenAI’s ChatGPT

