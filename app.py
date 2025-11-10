from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import models after db initialization (avoids circular import)
from models import Article

# Define routes
@app.route('/')
def home():
    articles = Article.query.all()
    return render_template('index.html', articles=articles)

# Entry point for local development
if __name__ == '__main__':
    app.run(debug=True)
