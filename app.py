from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import models AFTER db initialization
from models import Article

# Create database tables inside application context
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    articles = Article.query.all()
    return render_template('index.html', articles=articles)

if __name__ == '__main__':
    app.run(debug=True)
