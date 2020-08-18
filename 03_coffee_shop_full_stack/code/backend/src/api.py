import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import urllib.request
import urllib.parse
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# management api token availbele for 24h only starts from
MANG_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlhvRFNOcVM1TGp3NzdnekNLVm9oWSJ9.eyJpc3MiOiJodHRwczovL2Z3ZC1mc25kLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiI5SkkxS3g4eWRZV1QyM1U2dklCTlQwbGYzMElZU3dQdUBjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9md2QtZnNuZC51cy5hdXRoMC5jb20vYXBpL3YyLyIsImlhdCI6MTU5NjgyNDc2MCwiZXhwIjoxNTk2OTExMTYwLCJhenAiOiI5SkkxS3g4eWRZV1QyM1U2dklCTlQwbGYzMElZU3dQdSIsInNjb3BlIjoicmVhZDpjbGllbnRfZ3JhbnRzIGNyZWF0ZTpjbGllbnRfZ3JhbnRzIGRlbGV0ZTpjbGllbnRfZ3JhbnRzIHVwZGF0ZTpjbGllbnRfZ3JhbnRzIHJlYWQ6dXNlcnMgdXBkYXRlOnVzZXJzIGRlbGV0ZTp1c2VycyBjcmVhdGU6dXNlcnMgcmVhZDp1c2Vyc19hcHBfbWV0YWRhdGEgdXBkYXRlOnVzZXJzX2FwcF9tZXRhZGF0YSBkZWxldGU6dXNlcnNfYXBwX21ldGFkYXRhIGNyZWF0ZTp1c2Vyc19hcHBfbWV0YWRhdGEgcmVhZDp1c2VyX2N1c3RvbV9ibG9ja3MgY3JlYXRlOnVzZXJfY3VzdG9tX2Jsb2NrcyBkZWxldGU6dXNlcl9jdXN0b21fYmxvY2tzIGNyZWF0ZTp1c2VyX3RpY2tldHMgcmVhZDpjbGllbnRzIHVwZGF0ZTpjbGllbnRzIGRlbGV0ZTpjbGllbnRzIGNyZWF0ZTpjbGllbnRzIHJlYWQ6Y2xpZW50X2tleXMgdXBkYXRlOmNsaWVudF9rZXlzIGRlbGV0ZTpjbGllbnRfa2V5cyBjcmVhdGU6Y2xpZW50X2tleXMgcmVhZDpjb25uZWN0aW9ucyB1cGRhdGU6Y29ubmVjdGlvbnMgZGVsZXRlOmNvbm5lY3Rpb25zIGNyZWF0ZTpjb25uZWN0aW9ucyByZWFkOnJlc291cmNlX3NlcnZlcnMgdXBkYXRlOnJlc291cmNlX3NlcnZlcnMgZGVsZXRlOnJlc291cmNlX3NlcnZlcnMgY3JlYXRlOnJlc291cmNlX3NlcnZlcnMgcmVhZDpkZXZpY2VfY3JlZGVudGlhbHMgdXBkYXRlOmRldmljZV9jcmVkZW50aWFscyBkZWxldGU6ZGV2aWNlX2NyZWRlbnRpYWxzIGNyZWF0ZTpkZXZpY2VfY3JlZGVudGlhbHMgcmVhZDpydWxlcyB1cGRhdGU6cnVsZXMgZGVsZXRlOnJ1bGVzIGNyZWF0ZTpydWxlcyByZWFkOnJ1bGVzX2NvbmZpZ3MgdXBkYXRlOnJ1bGVzX2NvbmZpZ3MgZGVsZXRlOnJ1bGVzX2NvbmZpZ3MgcmVhZDpob29rcyB1cGRhdGU6aG9va3MgZGVsZXRlOmhvb2tzIGNyZWF0ZTpob29rcyByZWFkOmFjdGlvbnMgdXBkYXRlOmFjdGlvbnMgZGVsZXRlOmFjdGlvbnMgY3JlYXRlOmFjdGlvbnMgcmVhZDplbWFpbF9wcm92aWRlciB1cGRhdGU6ZW1haWxfcHJvdmlkZXIgZGVsZXRlOmVtYWlsX3Byb3ZpZGVyIGNyZWF0ZTplbWFpbF9wcm92aWRlciBibGFja2xpc3Q6dG9rZW5zIHJlYWQ6c3RhdHMgcmVhZDp0ZW5hbnRfc2V0dGluZ3MgdXBkYXRlOnRlbmFudF9zZXR0aW5ncyByZWFkOmxvZ3MgcmVhZDpzaGllbGRzIGNyZWF0ZTpzaGllbGRzIHVwZGF0ZTpzaGllbGRzIGRlbGV0ZTpzaGllbGRzIHJlYWQ6YW5vbWFseV9ibG9ja3MgZGVsZXRlOmFub21hbHlfYmxvY2tzIHVwZGF0ZTp0cmlnZ2VycyByZWFkOnRyaWdnZXJzIHJlYWQ6Z3JhbnRzIGRlbGV0ZTpncmFudHMgcmVhZDpndWFyZGlhbl9mYWN0b3JzIHVwZGF0ZTpndWFyZGlhbl9mYWN0b3JzIHJlYWQ6Z3VhcmRpYW5fZW5yb2xsbWVudHMgZGVsZXRlOmd1YXJkaWFuX2Vucm9sbG1lbnRzIGNyZWF0ZTpndWFyZGlhbl9lbnJvbGxtZW50X3RpY2tldHMgcmVhZDp1c2VyX2lkcF90b2tlbnMgY3JlYXRlOnBhc3N3b3Jkc19jaGVja2luZ19qb2IgZGVsZXRlOnBhc3N3b3Jkc19jaGVja2luZ19qb2IgcmVhZDpjdXN0b21fZG9tYWlucyBkZWxldGU6Y3VzdG9tX2RvbWFpbnMgY3JlYXRlOmN1c3RvbV9kb21haW5zIHVwZGF0ZTpjdXN0b21fZG9tYWlucyByZWFkOmVtYWlsX3RlbXBsYXRlcyBjcmVhdGU6ZW1haWxfdGVtcGxhdGVzIHVwZGF0ZTplbWFpbF90ZW1wbGF0ZXMgcmVhZDptZmFfcG9saWNpZXMgdXBkYXRlOm1mYV9wb2xpY2llcyByZWFkOnJvbGVzIGNyZWF0ZTpyb2xlcyBkZWxldGU6cm9sZXMgdXBkYXRlOnJvbGVzIHJlYWQ6cHJvbXB0cyB1cGRhdGU6cHJvbXB0cyByZWFkOmJyYW5kaW5nIHVwZGF0ZTpicmFuZGluZyBkZWxldGU6YnJhbmRpbmcgcmVhZDpsb2dfc3RyZWFtcyBjcmVhdGU6bG9nX3N0cmVhbXMgZGVsZXRlOmxvZ19zdHJlYW1zIHVwZGF0ZTpsb2dfc3RyZWFtcyBjcmVhdGU6c2lnbmluZ19rZXlzIHJlYWQ6c2lnbmluZ19rZXlzIHVwZGF0ZTpzaWduaW5nX2tleXMgcmVhZDpsaW1pdHMgdXBkYXRlOmxpbWl0cyIsImd0eSI6ImNsaWVudC1jcmVkZW50aWFscyJ9.K9PPLcu7S5ujSBqWnteSSgZtT1pH4-z8a51JBn-W-mhXgM7dfjij6tpeeYUrmOrZ-OtWN0uUoqFWSN2wE2Zun27A-ADzXKIM4dqJSyKp5wl90Stl3awbMfdgghH2JNivzSOvpS_2McB__9_iGTOi5yy1uWfBp8ytQqkprteg0gabSkFlGDDLcmFhmatbuck-kgNglkbpYHHJ6g2Jf64kJopv7rBzpMWGzIGPJFAI_YpuE7yVDPDkpC7QRMUvwF0YQp7DFfIp6huPGjXxdZdxhHGJXAGMg-Jj09l0OYgu-8tRVcjHvki37CpzDfftngdBZh9uQBW2562cevqRr0hhBQ"

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def return_drinks():
    drinks = Drink.query.all()
    if not drinks:
        abort(404)
    formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def return_drinks_detail(payload):
    drinks = Drink.query.all()
    if not drinks:
        abort(404)
    formatted_drinks = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    try:
        req = request.get_json()
        # turn json into string to be stored in database
        recipe = str(req['recipe'])
        # string is sent with single quotes which violates JSON principles so
        # its replaced with a double quotes
        recipe = recipe.replace("\'", "\"")
        new_drink = Drink(title=req['title'], recipe=recipe)
        new_drink.insert()
        return jsonify({
            "sucess": True,
            "drinks": new_drink.long()
        })
    except BaseException:
        raise


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink_info(payload, drink_id):
    drink = Drink.query.get(drink_id)
    req = request.get_json()
    if not drink:
        abort(404)
    try:
        # turn json into string to be stored in database
        recipe = str(req['recipe'])
        # string is sent with single quotes which violates JSON principles so
        # its replaced with a double quotes
        recipe = recipe.replace("\'", "\"")
        drink.recipe = recipe
    except BaseException:
        print("no recipe")
    drink.title = req['title']
    drink.update()
    return jsonify({
        'success': True,
        'drinks': [drink.short()]
    })


'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    drink.delete()
    return jsonify({
        'success': True,
        'drink_id': drink_id
    })


'''
    GET /baristas
        returns a list of all users assigned with the role barista
'''


@app.route('/baristas', methods=['GET'])
@requires_auth('get:baristas')
def get_baristas(payload):
    url = "https://fwd-fsnd.us.auth0.com/api/v2/roles/rol_lRvjhWQ9EQS6QFKr/users"
    hdr = {'authorization': "Bearer {}".format(MANG_TOKEN)}
    req = urllib.request.Request(url, headers=hdr)
    response = urllib.request.urlopen(req)
    return jsonify({
        "success": True,
        "data": response.read()
    })


'''
    POST /baristas/<id>/add
        assign the role Barista for the user of the given user_id
'''


@app.route('/baristas/<barista_id>', methods=['POST'])
@requires_auth('post:baristas')
def add_baristas(payload, barista_id):
    values = {"roles": ["rol_lRvjhWQ9EQS6QFKr"]}
    data = json.dumps(values)
    data = bytes(data.encode("utf-8"))
    url = "https://fwd-fsnd.us.auth0.com/api/v2/users/{}/roles".format(
        barista_id)
    hdr = {'authorization': "Bearer {}".format(MANG_TOKEN)}
    req = urllib.request.Request(url, data=data, headers=hdr)
    req.add_header("Content-type", "application/json; charset=UTF-8")
    return jsonify({
        "success": True,
        "barista_id": barista_id
    })


'''
    DELETE /baristas/<id>
        delete role Barista from the user of the given id

'''


@app.route('/baristas/<barista_id>', methods=['DELETE'])
@requires_auth('post:baristas')
def delete_baristas(payload, barista_id):
    values = {"roles": ["rol_lRvjhWQ9EQS6QFKr"]}
    data = json.dumps(values)
    data = bytes(data.encode("utf-8"))
    url = "https://fwd-fsnd.us.auth0.com/api/v2/users/{}/roles".format(
        barista_id)
    hdr = {'authorization': "Bearer {}".format(MANG_TOKEN)}
    req = urllib.request.Request(url, data=data, headers=hdr, method="DELETE")
    req.add_header("Content-type", "application/json; charset=UTF-8")
    return jsonify({
        "success": True,
        "barista_id": barista_id
    })


'''
    GET /managers
        returns a list of all users assigned with the role manager
'''


@app.route('/managers', methods=['GET'])
@requires_auth('get:managers')
def get_managers(payload):
    url = "https://fwd-fsnd.us.auth0.com/api/v2/roles/rol_njAOVPELGos8Y1x8/users"
    hdr = {'authorization': "Bearer {}".format(MANG_TOKEN)}
    req = urllib.request.Request(url, headers=hdr)
    response = urllib.request.urlopen(req)
    return jsonify({
        "success": True,
        "data": response.read()
    })


'''
    POST /managers/<id>/add
        assign the role Manager for the user of the given user_id
'''


@app.route('/managers/<manager_id>/add', methods=['POST'])
@requires_auth('post:managers')
def add_managers(payload, manager_id):
    values = {"roles": ["rol_njAOVPELGos8Y1x8"]}
    data = json.dumps(values)
    data = bytes(data.encode("utf-8"))
    url = "https://fwd-fsnd.us.auth0.com/api/v2/users/{}/roles".format(
        manager_id)
    hdr = {'authorization': "Bearer {}".format(MANG_TOKEN)}
    req = urllib.request.Request(url, data=data, headers=hdr)
    req.add_header("Content-type", "application/json; charset=UTF-8")
    response = urllib.request.urlopen(req)
    return jsonify({
        "success": True,
        "manager_id": manager_id
    })


'''
    DELETE /managers/<id>
        delete role Managers from the user of the given id

'''


@app.route('/managers/<manager_id>', methods=['DELETE'])
@requires_auth('post:managers')
def delete_managers(payload, manager_id):
    values = {"roles": ["rol_njAOVPELGos8Y1x8"]}
    data = json.dumps(values)
    data = bytes(data.encode("utf-8"))
    url = "https://fwd-fsnd.us.auth0.com/api/v2/users/{}/roles".format(
        manager_id)
    hdr = {'authorization': "Bearer {}".format(MANG_TOKEN)}
    req = urllib.request.Request(url, data=data, headers=hdr, method="DELETE")
    req.add_header("Content-type", "application/json; charset=UTF-8")
    response = urllib.request.urlopen(req)
    return jsonify({
        "success": True,
        "manager_id": manager_id
    })


# Error Handling
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
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@DONE implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500


'''
@DONE implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        "message": error.error
    }), error.status_code


@app.errorhandler(401)
def unathorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "access to the requested resource is forbidden"
    }), 403


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "this method is not allowed"
    }), 405
