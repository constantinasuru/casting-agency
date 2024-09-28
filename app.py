import os
from datetime import datetime

from flask import Flask, jsonify, abort, request

from auth import AuthError
from models import setup_db, db, Actor, Movie  # Import db from models
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

    @app.route('/actors', methods=['GET'])
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
    def get_actor(actor_id):
        actor = Actor.query.get(actor_id)
        if actor is None:
            abort(404)
        return jsonify({
            "success": True,
            "actor": actor.get_actor()
        })

    @app.route('/actors', methods=['POST'])
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
    def get_movie(movie_id):
        movie = Movie.query.get(movie_id)
        if movie is None:
            abort(404)
        return jsonify({
            "success": True,
            "movie": movie.get_movie()
        })

    @app.route('/movies', methods=['POST'])
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
    def not_found(error):
        return (jsonify({
            "success": False,
            "error": 400,
            "message": "Invalid input"
        }), 400)

    @app.errorhandler(403)
    def forbidden(error):
        return (jsonify({
            "success": False,
            "error": 403,
            "message": "You don't have the permission to access the requested resource."
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
