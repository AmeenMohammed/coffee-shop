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

## ROUTES
@app.route('/')
def index():
    return jsonify({
        'success': True,
        'message':"Hello you've made it to the coffee app ^_^"
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


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
