from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from app import db


class Article(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	headline = db.Column(db.String(512), nullable=False)
	original_url = db.Column(db.String(1024), unique=True, nullable=False)
	source_name = db.Column(db.String(128), nullable=False)
	region = db.Column(db.String(128), nullable=False, default="Uttar Pradesh")
	summary_en = db.Column(db.Text, nullable=True)
	summary_hi = db.Column(db.Text, nullable=True)
	sdg16_score = db.Column(db.Float, nullable=True)
	published_date = db.Column(db.DateTime, nullable=True, default=None)

	def __repr__(self) -> str:
		return f"<Article {self.id} {self.source_name}: {self.headline[:50]!r}>"


