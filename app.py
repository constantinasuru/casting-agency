import os
from flask import Flask, jsonify, abort, request

from auth import AuthError
from models import setup_db, db, Actor  # Import db from models
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
        print(result)
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
            db.session.delete(actor)
            db.session.commit()
            return jsonify({
                "success": True
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