from flask import Flask, render_template
from models import db, Article  # import db and model from models.py

def create_app():
    app = Flask(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize db with app
    db.init_app(app)

    # Create database tables within app context
    with app.app_context():
        db.create_all()

    # Define routes
    @app.route('/')
    def home():
        articles = Article.query.all()
        return render_template('index.html', articles=articles)

    return app

# Render looks for "app:app"
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
