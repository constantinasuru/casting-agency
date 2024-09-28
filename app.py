import os
from flask import Flask
from models import setup_db, db  # Import db from models
from flask_cors import CORS
from flask_migrate import Migrate  # Import Flask-Migrate

def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # Initialize Flask-Migrate with app and db
    migrate = Migrate(app, db)

    @app.route('/')
    def get_greeting():
        excited = os.getenv('EXCITED', 'false')
        greeting = "Hello"
        if excited == 'true':
            greeting = greeting + "!!!!! You are doing great in this Udacity project."
        return greeting

    @app.route('/coolkids')
    def be_cool():
        return "Be cool, man, be coooool! You're almost a FSND grad!"

    return app

app = create_app()

if __name__ == '__main__':
    app.run()