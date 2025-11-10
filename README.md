# LokSamvaad (MVP)

## Setup

1. Create venv and install deps (already done if using Cursor steps):

```bash
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

2. Set environment variable for Gemini API:

```powershell
$env:GEMINI_API_KEY = "AIzaSyBHUBR9PC7At5TX_cCYlwM85T-tJB-RmZ0"
```

3. Run the Flask app:

```bash
python app.py
```

Then open http://localhost:5000

## Scrape and process articles

Run the scraper to populate the database:

```bash
python scraper.py
```

This will scrape The Hindu and Dainik Jagran, classify for SDG 16, and summarize in English and Hindi.

## Notes
- Database: SQLite file `news.db` in the project root.
- API: `GET /api/articles` returns all articles as JSON.

