from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from models import Article
db.create_all()

from models import Article  # Import AFTER db initialization

@app.route('/')
def home():
    articles = Article.query.all()
    return render_template('index.html', articles=articles)

if __name__ == '__main__':
    app.run(debug=True)
