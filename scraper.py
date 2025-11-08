import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

from app import create_app, db
from models import Article


def _get(url: str, timeout: int = 20) -> Optional[requests.Response]:
	try:
		resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
		resp.raise_for_status()
		return resp
	except Exception:
		return None


def scrape_news_sources() -> List[Tuple[str, str, str, Optional[datetime]]]:
	"""
	Scrape headlines and URLs from The Hindu (English) and Dainik Jagran (Hindi)
	sections: National and Uttar Pradesh.

	Returns a list of tuples: (headline, url, source_name, published_date)
	"""
	results: List[Tuple[str, str, str, Optional[datetime]]] = []

	# The Hindu - National
	for url in [
		"https://www.thehindu.com/news/national/",
		"https://www.thehindu.com/news/national/other-states/uttar-pradesh/",
	]:
		resp = _get(url)
		if not resp:
			continue
		soup = BeautifulSoup(resp.text, "html.parser")
		for a in soup.select("a.story-card75x1-text, a.title, a.card-title, a.story-card a"):
			href = a.get("href") or ""
			head = (a.get_text(strip=True) or "").strip()
			if not href or not head:
				continue
			if href.startswith("/"):
				href = "https://www.thehindu.com" + href
			results.append((head, href, "The Hindu", None))

	# Dainik Jagran - National & Uttar Pradesh
	for url in [
		"https://www.jagran.com/national-news-hindi.html",
		"https://www.jagran.com/uttar-pradesh.htm",
	]:
		resp = _get(url)
		if not resp:
			continue
		soup = BeautifulSoup(resp.text, "html.parser")
		for a in soup.select("a, h3 a, .hnews a, .list-article a"):
			href = a.get("href") or ""
			head = (a.get_text(strip=True) or "").strip()
			if not href or not head:
				continue
			if href.startswith("/"):
				href = "https://www.jagran.com" + href
			# basic filter to skip nav or empty anchors
			if not href.startswith("http") or len(head) < 10:
				continue
			results.append((head, href, "Dainik Jagran", None))

	# Times of India - India & Lucknow
	for url in [
		"https://timesofindia.indiatimes.com/india",
		"https://timesofindia.indiatimes.com/city/lucknow",
	]:
		resp = _get(url)
		if not resp:
			continue
		soup = BeautifulSoup(resp.text, "html.parser")
		for a in soup.select("h2 a, h3 a, a"):
			href = a.get("href") or ""
			head = (a.get_text(strip=True) or "").strip()
			if not href or not head or len(head) < 10:
				continue
			if href.startswith("/"):
				href = "https://timesofindia.indiatimes.com" + href
			if not href.startswith("https://timesofindia.indiatimes.com"):
				continue
			results.append((head, href, "Times of India", None))

	# The Indian Express - India & Lucknow
	for url in [
		"https://indianexpress.com/section/india/",
		"https://indianexpress.com/section/cities/lucknow/",
	]:
		resp = _get(url)
		if not resp:
			continue
		soup = BeautifulSoup(resp.text, "html.parser")
		for a in soup.select("h2 a, h3 a, .title a, .heading a, a"):
			href = a.get("href") or ""
			head = (a.get_text(strip=True) or "").strip()
			if not href or not head or len(head) < 10:
				continue
			if href.startswith("/"):
				href = "https://indianexpress.com" + href
			if not href.startswith("https://indianexpress.com"):
				continue
			results.append((head, href, "Indian Express", None))

	# Amar Ujala - India & Uttar Pradesh
	for url in [
		"https://www.amarujala.com/india-news",
		"https://www.amarujala.com/uttar-pradesh",
	]:
		resp = _get(url)
		if not resp:
			continue
		soup = BeautifulSoup(resp.text, "html.parser")
		for a in soup.select("h2 a, h3 a, .list a, a"):
			href = a.get("href") or ""
			head = (a.get_text(strip=True) or "").strip()
			if not href or not head or len(head) < 10:
				continue
			if href.startswith("/"):
				href = "https://www.amarujala.com" + href
			if not href.startswith("https://www.amarujala.com"):
				continue
			results.append((head, href, "Amar Ujala", None))

	return results


def _init_genai() -> None:
	api_key = os.environ.get("GEMINI_API_KEY")
	if not api_key:
		raise RuntimeError("GEMINI_API_KEY environment variable is not set")
	genai.configure(api_key=api_key)


def _call_gemini_json(prompt: str, content: str) -> Dict:
	model = genai.GenerativeModel("models/gemini-2.5-flash")

	response = model.generate_content([
		{"role": "user", "parts": [prompt, "\n\n", content]},
	])
	text = (response.text or "").strip()
	# Extract JSON object using a simple fallback
	match = re.search(r"\{[\s\S]*\}", text)
	if match:
		text = match.group(0)
	try:
		import json
		return json.loads(text)
	except Exception:
		return {"is_related": False, "score": 0.0}


def _call_gemini_text(prompt: str, content: str) -> str:
	model = genai.GenerativeModel("models/gemini-2.5-flash")
	response = model.generate_content([
		{"role": "user", "parts": [prompt, "\n\n", content]},
	])
	return (response.text or "").strip()


def process_article(headline: str, article_text: str) -> Tuple[Optional[str], Optional[str], float]:
	print(f"   🔹 Analyzing: {headline[:80]}")

	"""
	Returns: (summary_en, summary_hi, sdg16_score)
	"""
	_init_genai()

	classification_prompt = (
		"Analyze the following news headline and text. Is this article related to SDG 16: "
		"Peace, Justice, and Strong Institutions? Topics include court rulings, new laws, "
		"government policy, police actions, anti-corruption efforts, human rights, or public "
		"institution reforms. Respond only with a JSON object like: {\"is_related\": true/false, \"score\": 0.0-1.0}"
	)
	classification = _call_gemini_json(classification_prompt, f"Headline: {headline}\n\nText: {article_text}")
	is_related = bool(classification.get("is_related"))
	score = float(classification.get("score", 0.0) or 0.0)

	if not is_related or score <= 0.6:
		return None, None, score

	summarize_prompt = (
		"You are an objective news assistant. Summarize the following article for a general citizen. "
		"Provide a neutral 1-sentence summary and then 3 key bullet points. First, write the output in English. "
		"Then, translate the entire output (summary and bullets) into Hindi."
	)
	full_text = f"Headline: {headline}\n\nArticle: {article_text}"
	combined_output = _call_gemini_text(summarize_prompt, full_text)

	# Split English and Hindi heuristically if model uses clear separation
	# Otherwise, store entire combined output in both fields appropriately parsed
	parts = re.split(r"\n\s*Hindi\s*:|\n\s*हिंदी\s*:", combined_output, flags=re.IGNORECASE)
	if len(parts) >= 2:
		summary_en = parts[0].strip()
		summary_hi = parts[1].strip()
	else:
		# Fallback: attempt simple bilingual structure by duplicating
		summary_en = combined_output
		summary_hi = combined_output

	return summary_en, summary_hi, score


def _extract_article_text(url: str) -> str:
	resp = _get(url)
	if not resp:
		return ""
	soup = BeautifulSoup(resp.text, "html.parser")
	paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
	text = "\n".join([p for p in paragraphs if len(p) > 40])
	return text[:8000]  # keep prompt size modest


def run_scraper() -> None:
    app = create_app()
    with app.app_context():
        items = scrape_news_sources()
        print(f"📰 Total scraped headlines: {len(items)}")

        seen_urls = {u for (u,) in db.session.query(Article.original_url).all()}
        print(f"🧾 Already in database: {len(seen_urls)} URLs")

        for i, (headline, url, source_name, published_date) in enumerate(items, start=1):
            if url in seen_urls:
                continue

            print(f"\n[{i}/{len(items)}] Fetching article from {source_name}: {headline[:60]}...")
            article_text = _extract_article_text(url)

            if not article_text:
                print("⚠️ Skipped (no article text).")
                continue

            try:
                summary_en, summary_hi, score = process_article(headline, article_text)
                print(f"🔍 SDG16 Score: {score}")
            except Exception as e:
                print(f"❌ Error in processing article: {e}")
                continue

            if summary_en and summary_hi:
                print("✅ Related to SDG 16 — saving to DB...")
                row = Article(
                    headline=headline[:512],
                    original_url=url[:1024],
                    source_name=source_name,
                    region="Uttar Pradesh",
                    summary_en=summary_en,
                    summary_hi=summary_hi,
                    sdg16_score=score,
                    published_date=published_date or datetime.utcnow(),
                )
                db.session.add(row)
                try:
                    db.session.commit()
                    seen_urls.add(url)
                except Exception as e:
                    print(f"⚠️ Database commit failed: {e}")
                    db.session.rollback()
            else:
                print("❌ Not related to SDG 16 — skipped.")


# (All your import statements and function definitions go above)

if __name__ == "__main__":
	print("--- My scraper script is starting! ---")
	
	run_scraper()  # Run the actual scraper entry point

	print("--- My scraper script has finished! ---")

# Note: run_scraper() is the intended entry point; there is no `main()` function.


