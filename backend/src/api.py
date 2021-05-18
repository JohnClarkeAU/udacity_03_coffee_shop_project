import os
import logging
import logging.config
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import (Drink,
                              setup_db, db_drop_and_create_all, db_rollback)
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# Set up logging
logging.config.fileConfig(fname='logfile.conf', disable_existing_loggers=False)

# Get the logger specified in the file
logger = logging.getLogger(__name__)
logger.debug('STARTING the Coffee Shop backend')

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES


@app.route('/')
def index():
    '''
    GET / is a public endpoint that displays 'Welcome to the Coffee Shop'.

    This is normally just used to check if the web server is responding.

    Returns
        status code 200 and the html text 'Welcome to the Coffee Shop'
    '''
    return 'Welcome to the Coffee Shop'


@app.route('/drinks', methods=['GET'])
def drinks():
    '''
    GET /drinks is a public endpoint returning a list of drinks.

    This is used to get a list of drinks in the drink.short() data format
    and is used to display the names and colours of the drinks.

    Returns
        status code 200 and json {"success": True, "drinks": drinks}
            where drinks is the list of drinks
        status code 404 if there are no drinks
        status code 422 if there is a database error
    '''
    logger.debug('GET /drinks')
    # get all the drinks
    try:
        all_drinks = Drink.query.all()
    except Exception as e:
        abort(422, "Unexpected error accessing the database.")

    # return a 404 error if there are no drinks
    if len(all_drinks) is 0:
        abort(404, 'There are no drinks')

    # get the short form of the drinks list
    drinks = [drink.short() for drink in all_drinks]

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    '''
    GET /drinks-detail is a protected endpoint returning a list of drinks.

    This is used to get a list of drinks in the drink.long() data format
    and is used to display the recipes for each of the drinks.

    Requires the 'get:drinks-detail' permission.

    Returns
        status code 200 and json {"success": True, "drinks": drinks}
            where drinks is the list of drinks in the drink.long() data format
        status code 400 if there are no permissions in the JWT
        status code 401 if the user does not have permission to do this
        status code 404 if there are no drinks
        status code 422 if there is a database error
    '''
    logger.debug('GET /drinks-detail')
    # get all the drinks
    try:
        all_drinks = Drink.query.all()
    except Exception as e:
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


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def drinks_create(jwt):
    '''
    POST /drinks is an endpoint to create a new row in the drinks table.

    This is used to add a new drink to the drinks table using the data
    supplied in the drink.long() data representation.

    A drink with the same title must not already be in the drinks table.

    Requires the 'post:drinks' permission.

    Returns
        status code 200 and json {"success": True, "drinks": drink}
            where drink is an array containing only the newly created drink
        status code 400 if there is an error in the submitted data
        status code 400 if there are no permissions in the JWT
        status code 401 if the user does not have the required permission
        status code 422 if there is a database error
    '''
    logger.debug('POST/drinks')

    # get the input data
    try:
        body = dict(request.form or request.json or request.data)
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)
    except Exception as e:
        abort(400, "Invalid input data. (title and recipe are required.)")

    # check that all fields have been submitted
    if new_title is None and new_recipe is None:
        abort(400, "Missing input field(s). (title and recipe are required.)")
    if new_title is None:
        abort(400, "Missing input field(s). (title is required.)")
    if new_recipe is None:
        abort(400, "Missing input field(s). (recipe is required.)")

    # check that none of the fields are blank
    if new_title == '':
        abort(400, description="The title must not be blank.")
    if new_recipe == '':
        abort(400, description="The recipe must not be blank.")

    # ensure that the title is unique
    existing_drink = Drink.query.filter(Drink.title == new_title).one_or_none()
    if existing_drink is not None:
        abort(400, description="Cannot add '" + new_title +
              "'. That drink already exists in the datbase.")
    try:
        # start of a rollbackable transaction
        # insert the new drink
        drink = Drink(
            title=new_title,
            recipe=json.dumps(new_recipe)
        )
        drink.insert()
        # return the long form of the drink just inserted
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception as e:
        db_rollback()
        abort(422, "Unexpected error inserting the drink into the database.")


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def drinks_patch(jwt, id):
    '''
    PATCH /drinks/<id> is an endpoint to update the corresponding row for <id>.

    This is used to amend a drink in the drinks table using the data
    supplied in the drink.long() data representation.

    A drink with the same <id> must already be in the drinks table otherwise a
    404 error is returned if <id> is not found in the drinks table.

    Requires the 'patch:drinks' permission.

    Returns
        status code 200 and json {"success": True, "drinks": drink}
            where drink is an array containing only the updated drink
        status code 400 if there is an error in the submitted data
        status code 400 if there are no permissions in the JWT
        status code 401 if the user does not have permission to do this
        status code 404 if <id> is not found in the database
        status code 422 if there is a database error
    '''
    logger.debug('PATCH/drinks/' + str(id))

    # get the input data
    try:
        body = dict(request.form or request.json or request.data)
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)
    except Exception as e:
        abort(400, "Invalid input data. ", e.__class__,
              " (title or recipe are required.)")

    # check that at least one of title and recipe has been supplied
    if new_title is None and new_recipe is None:
        abort(400, "Missing input field(s). (title or recipe are required.)")

    if new_title == '' or new_recipe == '':
        abort(400, "Bad input field(s). (title or recipe must not be blank.)")

    # get the drink to patch
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404, "id not found in the database.")

    try:
        # start of a rollbackable transaction
        # insert the new data to the drink
        if new_title is not None:
            drink.title = new_title
        if new_recipe is not None:
            drink.recipe = json.dumps(new_recipe)
        drink.update()

        # return the long form of the drink just inserted
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    except Exception as e:
        db_rollback()
        abort(422, "Unexpected error updating the database.")


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def drinks_delete(jwt, id):
    '''
    DELETE /drinks/<id> is an endpoint to delete the existing row for <id>.

    This is used to delete a drink from the drinks table using the <id>
    supplied.

    A drink with the same <id> must already be in the drinks table otherwise a
    404 error is returned if <id> is not found in the drinks table.

    Requires the 'delete:drinks' permission.

    Returns
        status code 200 and json {"success": True, "delete": id}
            where id is the id of the deleted record
        status code 400 if there are no permissions in the JWT
        status code 401 if the user does not have permission to do this
        status code 404 if <id> is not found in the database
        status code 422 if there is a database error
    '''
    logger.debug('DELETE/drinks/' + str(id))

    # get the drink to be deleted
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404, "id '" + str(id) + "' not found in the database.")
    try:
        # start of a rollbackable transaction
        # delete the drink from the database
        drink.delete()

        # return the id of the deleted item
        return jsonify({
            'success': True,
            'delete': id
        }), 200

    except Exception as e:
        db_rollback()
        abort(422, "Unexpected error deleting the drink from the database.")


# ERROR HANDLING

@app.errorhandler(AuthError)
def handle_auth_error_json(error):
    # logger.debug('AuthError:',error)
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
