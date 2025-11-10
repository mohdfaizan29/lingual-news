from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Just define db here — no import from app
db = SQLAlchemy()

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(512))
    original_url = db.Column(db.String(1024))
    source_name = db.Column(db.String(256))
    region = db.Column(db.String(128))
    summary_en = db.Column(db.Text)
    summary_hi = db.Column(db.Text)
    sdg16_score = db.Column(db.Float)
    published_date = db.Column(db.DateTime, default=datetime.utcnow)


	def __repr__(self) -> str:
		return f"<Article {self.id} {self.source_name}: {self.headline[:50]!r}>"


