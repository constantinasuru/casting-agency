import os
from datetime import datetime

from flask import Flask, jsonify, abort, request, redirect, url_for, session

from auth import AuthError, requires_auth
from models import setup_db, db, Actor, Movie  # Import db from models
from flask_cors import CORS
from flask_migrate import Migrate  # Import Flask-Migrate


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # Initialize Flask-Migrate with app and db
    migrate = Migrate(app, db)

    AUTH0_DOMAIN = 'dev-tool.eu.auth0.com'
    API_IDENTIFIER = 'casting'
    CLIENT_ID = 'ePggLb2HCSsTOfDujcbMhIeH7Yk1o6fP'
    CLIENT_SECRET = 'Z67vW6Fw4ihnJzrBS1QZmt5CwGTKOQkP9e5u_tfbSO5wiWrRPWNn0l1XSOkQnEEH'
    REDIRECT_URI = 'http://127.0.0.1:5000/'

    app.secret_key = 'fsda'  # Change this to a random secret key

    @app.route('/login')
    def login():
        return redirect(f'https://{AUTH0_DOMAIN}/authorize?'
                        f'audience={API_IDENTIFIER}&'
                        f'client_id={CLIENT_ID}&'
                        f'response_type=token&'
                        f'redirect_uri={REDIRECT_URI}')

    @app.route('/callback')
    def callback():
        # This route will be called by Auth0 after the user logs in
        # You will typically get the access token here from the URL
        access_token = request.args.get('access_token')
        session['access_token'] = access_token
        return redirect(url_for('dashboard'))

    @app.route('/dashboard')
    def dashboard():
        access_token = session.get('access_token')
        if not access_token:
            return redirect(url_for('login'))

        # Here you can use the access token to make authenticated requests
        return jsonify({
            'message': 'Welcome to the dashboard!',
            'access_token': access_token
        })

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

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors():
        result = Actor.query.all()
        if not result:
            abort(404)
        actors = []
        for actor in result:
            actors.append(actor.get_actor())
        return jsonify({
            "success": True,
            "actors": actors
        })

    @app.route('/actors/<int:actor_id>', methods=['GET'])
    @requires_auth('get:actors')
    def get_actor(actor_id):
        actor = Actor.query.get(actor_id)
        if actor is None:
            abort(404)
        return jsonify({
            "success": True,
            "actor": actor.get_actor()
        })

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def create_actor():
        body = request.get_json()
        name = body.get('name')
        age = body.get('age')
        gender = body.get('gender')
        if not name or not age or not gender:
            abort(400)
        try:
            actor = Actor(name=name, age=age, gender=gender)
            db.session.add(actor)
            db.session.commit()
            return jsonify({
                "success": True,
                "actor": actor.get_actor()
            })
        except:
            db.session.rollback()
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actor(actor_id):
        body = request.get_json()
        name = body.get('name')
        age = body.get('age')
        gender = body.get('gender')
        try:
            actor = Actor.query.get(actor_id)
            print(actor)
            if actor is None:
                abort(404)
            if name:
                actor.name = name
            if age:
                actor.age = age
            if gender:
                actor.gender = gender
            print(actor.get_actor())
            db.session.commit()
            return jsonify({
                "success": True,
                "actor": actor.get_actor()
            })
        except:
            db.session.rollback()
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(actor_id):
        actor = Actor.query.get(actor_id)
        if actor is None:
            abort(404)
        try:
            for movie in actor.movies:
                movie.actors.remove(actor)
            db.session.delete(actor)
            db.session.commit()
            return jsonify({
                "success": True
            })
        except:
            db.session.rollback()
            abort(422)

    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies():
        result = Movie.query.all()
        if not result:
            abort(404)
        movies = []
        for movie in result:
            movies.append(movie.get_movie())
        return jsonify({
            "success": True,
            "movies": movies
        })

    @app.route('/movies/<int:movie_id>', methods=['GET'])
    @requires_auth('get:movies')
    def get_movie(movie_id):
        movie = Movie.query.get(movie_id)
        if movie is None:
            abort(404)
        return jsonify({
            "success": True,
            "movie": movie.get_movie()
        })

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def create_movie():
        body = request.get_json()
        title = body.get('title')
        release_date_str = body.get('release_date')
        if not title or not release_date_str:
            abort(400)
        try:
            release_date = datetime.fromisoformat(release_date_str)
            movie = Movie(title=title, release_date=release_date)
            db.session.add(movie)
            db.session.commit()
            return jsonify({
                "success": True,
                "movie": movie.get_movie()
            })
        except ValueError:
            abort(400, description="Invalid date format. Use ISO 8601 format e.g., '2023-09-28T14:30:00")
        except:
            db.session.rollback()
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(movie_id):
        body = request.get_json()
        title = body.get('title')
        release_date_str = body.get('release_date')
        try:
            movie = Movie.query.get(movie_id)
            if movie is None:
                abort(404)
            if title:
                movie.title = title
            if release_date_str:
                movie.release_date = datetime.fromisoformat(release_date_str)
            db.session.commit()
            return jsonify({
                "success": True,
                "movie": movie.get_movie()
            })

        except ValueError:
            abort(400, description="Invalid date format. Use ISO 8601 format e.g., '2023-09-28T14:30:00")
        except:
            db.session.rollback()
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(movie_id):
        try:
            movie = Movie.query.get(movie_id)
            if movie is None:
                abort(404)
            for actor in movie.actors:
                actor.movies.remove(movie)
            db.session.delete(movie)
            db.session.commit()
            return jsonify({
                "success": True
            })
        except:
            db.session.rollback()
            abort(422)

    @app.route('/movies/<int:movie_id>/actors', methods=['POST'])
    @requires_auth('patch:movies')
    def link_movie_to_actors(movie_id):
        movie = Movie.query.get(movie_id)
        if not movie:
            abort(404)

        body = request.get_json()
        actor_ids = body.get('actor_ids', [])
        try:
            movie.actors.clear()
            for actor_id in actor_ids:
                actor = Actor.query.get(actor_id)
                if actor:
                    movie.actors.append(actor)
            db.session.commit()
            return jsonify({
                "success": True,
                "movie": movie.get_movie()
            })
        except:
            db.session.rollback()
            abort(422)


    @app.errorhandler(422)
    def unprocessable(error):
        return (jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422)

    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404)

    @app.errorhandler(400)
    def bad_request(error):
        return (jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400)

    @app.errorhandler(401)
    def unauthorised(error):
        return (jsonify({
            "success": False,
            "error": 401,
            "message": "Unauthorized"
        }), 401)

    @app.errorhandler(403)
    def forbidden(error):
        return (jsonify({
            "success": False,
            "error": 403,
            "message": "You don't have the permission to access the requested resource."
        }), 403)

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed."
        }), 403)

    @app.errorhandler(AuthError)
    def handle_auth_error(e):
        response = jsonify(e.error)
        response.status_code = e.status_code
        return response

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
