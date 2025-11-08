async function fetchArticles() {
	try {
		const res = await fetch('/api/articles');
		if (!res.ok) throw new Error('Failed to fetch articles');
		return await res.json();
	} catch (e) {
		console.error(e);
		return [];
	}
}

function createCard(article) {
	const col = document.createElement('div');
	col.className = 'card';

	const body = document.createElement('div');
	body.className = 'card-body';

	const h5 = document.createElement('h5');
	h5.className = 'card-title';
	h5.textContent = article.headline || 'Untitled';

	const meta = document.createElement('div');
	meta.className = 'meta mb-2';
	const dateText = article.published_date ? new Date(article.published_date).toLocaleString() : '';
	meta.textContent = `${article.source_name || ''} ${dateText ? '· ' + dateText : ''}`;

	const a = document.createElement('a');
	a.href = article.original_url;
	a.target = '_blank';
	a.rel = 'noopener noreferrer';
	a.textContent = 'Read original';
	a.className = 'btn btn-sm btn-outline-primary me-2';

	const score = document.createElement('span');
	score.className = 'badge text-bg-secondary';
	score.textContent = typeof article.sdg16_score === 'number' ? `SDG16 ${article.sdg16_score.toFixed(2)}` : 'SDG16 -';

	const summaryEn = document.createElement('div');
	summaryEn.className = 'summary-en mt-2';
	summaryEn.textContent = article.summary_en || '';

	const summaryHi = document.createElement('div');
	summaryHi.className = 'summary-hi mt-2';
	summaryHi.textContent = article.summary_hi || '';

	body.appendChild(h5);
	body.appendChild(meta);
	body.appendChild(a);
	body.appendChild(score);
	body.appendChild(summaryEn);
	body.appendChild(summaryHi);

	col.appendChild(body);
	return col;
}

function toggleLanguage(showHindi) {
	const enNodes = document.querySelectorAll('.summary-en');
	const hiNodes = document.querySelectorAll('.summary-hi');
	enNodes.forEach(n => { n.style.display = showHindi ? 'none' : ''; });
	hiNodes.forEach(n => { n.style.display = showHindi ? '' : 'none'; });
}

document.addEventListener('DOMContentLoaded', async () => {
	const feed = document.getElementById('news-feed');
	const data = await fetchArticles();
	feed.innerHTML = '';
	if (!data.length) {
		feed.innerHTML = '<div class="alert alert-info">No articles yet. Run the scraper to populate data.</div>';
		return;
	}
	data.forEach(article => feed.appendChild(createCard(article)));

	const toggle = document.getElementById('langToggle');
	toggle.addEventListener('change', (e) => toggleLanguage(e.target.checked));
});


