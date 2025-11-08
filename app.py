from flask import Flask, render_template, request
from models import db, Article
from dotenv import load_dotenv

import os

load_dotenv()

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///news.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.route("/")
def home():
    query = Article.query

    # Filters
    region = request.args.get("region")
    source = request.args.get("source")
    language = request.args.get("lang")

    if region:
        query = query.filter(Article.region.ilike(f"%{region}%"))
    if source:
        query = query.filter(Article.source_name.ilike(f"%{source}%"))

    articles = query.order_by(Article.published_date.desc()).limit(50).all()
    return render_template("index.html", articles=articles, region=region, source=source, language=language)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
