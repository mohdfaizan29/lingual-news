from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(255), nullable=False)
    original_url = db.Column(db.String(500))
    source_name = db.Column(db.String(100))
    region = db.Column(db.String(50))
    summary_en = db.Column(db.Text)
    summary_hi = db.Column(db.Text)
    sdg16_score = db.Column(db.Float)
    published_date = db.Column(db.String(50))
