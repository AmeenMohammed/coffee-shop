import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES


@app.route('/')
def index():
    return jsonify({
        'success': True,
        'message': "Hello you've made it to the coffee app ^_^"
    })


@app.route("/drinks")
def get_drinks():
    drinks = list(map(Drink.short, Drink.query.all()))
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(jwt):
    drinks = list(map(Drink.long, Drink.query.all()))
    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(jwt):
    data = request.get_json()

    if 'title' and 'recipe' not in data:
        abort(422)

    title = data.get('title', None)
    recipe = data.get('recipe', None)

    drink = Drink(title=title, recipe=json.dumps(recipe))
    Drink.insert(drink)

    added_drink = Drink.query.filter_by(id=drink.id).first()

    return jsonify({
        'success': True,
        'drinks': [added_drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)

    if drink is None:
        abort(404)

    data = request.get_json()

    if 'title' in data:
        drink.title = data.get('title', None)

    if 'recipe' in data:
        drink.recipe = json.dumps(data.get('recipe', None))

    drink.update()

    edited_drink = Drink.query.filter_by(id=drink_id).first()

    return jsonify({
        'success': True,
        'drinks': [edited_drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink.id
    })


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found_404(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(AuthError)
def process_AuthError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code

    return response
