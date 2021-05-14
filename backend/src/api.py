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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
@app.route('/')
def index():
    return 'Welcome to the Coffee Shop'

'''
GET /drinks
    is a public endpoint
    reesponse contains only the drink.short() data representation
returns 
    status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
    status code 404 if there are no drinks
    status code 422 if there is a database error
'''

@app.route('/drinks', methods=['GET'])
def drinks():
    print('GET /drinks')
    # get all the drinks
    try:
        all_drinks = Drink.query.all()
    except:
        abort(422, "Unexpected error accessing the database.")

    # return an error if there are no drinks
    if len(all_drinks) is 0:
        abort(404, 'There are no drinks')
    
    # get the short form of the drinks list
    drinks = [drink.short() for drink in all_drinks]

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200

'''
GET /drinks-detail
    requires the 'get:drinks-detail' permission
    response contains  the drink.long() data representation
returns 
    status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
    status code 400 if there are no permissions in the JWT
    status code 401 if the user does not have permission to do this transaction
    status code 404 if there are no drinks
    status code 422 if there is a database error
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    print('GET /drinks_detail')
    # get all the drinks
    try:
        all_drinks = Drink.query.all()
    except:
        abort(422, "Unexpected error accessing the database.")
    
    # return an error if there are no drinks
    if len(all_drinks) is 0:
        abort(404, 'There are no drinks')
    
    # get the short form of the drinks list
    drinks = [drink.long() for drink in all_drinks]

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200

'''
POST /drinks
    requires the 'post:drinks' permission
    creates a new row in the drinks table
    the POST should contain the drink.long() data representation
returns 
    status code 200 and json {"success": True, "drinks": drink} where drink is an array containing only the newly created drink
    status code 400 if there is an error in the submitted data
    status code 400 if there are no permissions in the JWT
    status code 401 if the user does not have permission to do this transaction
    status code 422 if there is a database error
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def drinks_create(jwt):
    print('POST/drinks')

    # get the input data
    try:
        body = dict(request.form or request.json or request.data)
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)
    except:
        abort(400, "Invalid input data. (title and recipe must be supplied.)")

    # check that all fields have been submitted
    if new_title is None and new_recipe is None:
        abort(400, "Missing input field(s). (title and recipe must be supplied.)")
    if new_title is None:
        abort(400, "Missing input field(s). (title must be supplied.)")
    if new_recipe is None:
        abort(400, "Missing input field(s). (recipe must be supplied.)")
    
    # check that none of the fields are blank
    if new_title == '':
        abort(400, description="None of the fields may be blank. (title must be supplied.)")
    if new_recipe == '':
        abort(400, description="None of the fields may be blank. (recipe must be supplied.)")

    # need to check that the drink does not already exist

    try:
        # insert the new drink
        drink = Drink(
            title = new_title,
            recipe = json.dumps(new_recipe)
        )
        drink.insert()
    except:
        abort(422, "Unexpected error inserting the drink into the database.")

    # return the long form of the drink just inserted
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200

'''
PATCH /drinks/<id>
    where <id> is the existing model id
    requires the 'patch:drinks' permission
    updates the corresponding row for <id>
    responds with a 404 error if <id> is not found
    the PATCH should contain the drink.long() data representation
returns 
    status code 200 and json {"success": True, "drinks": drink} where drink is an array containing only the updated drink
    status code 400 if there is an error in the submitted data
    status code 400 if there are no permissions in the JWT
    status code 401 if the user does not have permission to do this transaction
    status code 404 if <id> is not found in the database
    status code 422 if there is a database error
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def drinks_patch(jwt, id):
    print('PATCH/drinks/', id)

    # get the input data
    try:
        body = dict(request.form or request.json or request.data)
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)
    except:
        abort(400, "Invalid input data. (title or recipe must be supplied.)")

    # check that at least one of title and recipe has been supplied
    if new_title is None and new_recipe is None:
        abort(400, "Missing input field(s). (title or recipe must be supplied.)")

    if new_title == '' or new_recipe == '':
        abort(400, "Bad input field(s). (title or recipe must not be blank.)")

    drink = []
    try:
        # get the drink to patch
        drink = Drink.query.filter(Drink.id == id).one_or_none()
    except:
        abort(422, "Unexpected error accessing the database.")

    if drink is None:
        abort(404, "id not found in the database.")

    try:
        # insert the new data to the drink
        if new_title != None:
            drink.title = new_title
        if new_recipe != None:
            drink.recipe = json.dumps(new_recipe)
        drink.update()
    except:
        abort(422, "Unexpected error updating the database.")

    # return the long form of the drink just inserted
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200

'''
DELETE /drinks/<id>
    where <id> is the existing model id
    requires the 'delete:drinks' permission
    deletes the corresponding row for <id>
    responds with a 404 error if <id> is not found
returns 
    status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
    status code 400 if there are no permissions in the JWT
    status code 401 if the user does not have permission to do this transaction
    status code 404 if <id> is not found in the database
    status code 422 if there is a database error
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def drinks_delete(jwt, id):
    print('DELETE/drinks/', id)

    # get the drink to be deleted
    drink = []
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
    except:
        abort(422, "Unexpected error accessing the database.")

    if drink is None:
        abort(404, "id not found in the database.")

    # delete the drink
    try:
        drink.delete()
    except:
        abort(422, "Unexpected error deleting the drink from the database.")

    return jsonify({
        'success': True,
        'delete': id
    }), 200

    # # for debugging 
    # # comment out the previous return and uncomment out this section
    # # to display all drinks left in the database
    # # get all the drinks
    # all_drinks = Drink.query.all()
    
    # # return an error if there are no drinks
    # if len(all_drinks) is 0:
    #     abort(404, 'There are no drinks')
    
    # # get the long form of the drinks list
    # drinks = [drink.long() for drink in all_drinks]

    # return jsonify({
    #     'success': True,
    #     'drinks': drinks
    # }), 200

## Error Handling

@app.errorhandler(AuthError)
def handle_auth_error_json(error):
    # print('AuthError:',error)
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": str(error.error['description'])
    }), error.status_code

@app.errorhandler(400)
def bad_request_error_json(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": str(error)
    }), 400

@app.errorhandler(401)
def unauthorized_error_json(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": str(error)
    }), 401

@app.errorhandler(404)
def not_found_error_json(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": str(error)
    }), 404

@app.errorhandler(405)
def method_not_allowed_error_json(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405

@app.errorhandler(422)
def unprocessable_error_json(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": str(error)
    }), 422

@app.errorhandler(500)
def internal_error_json(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Error"
    }), 500
