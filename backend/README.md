# Coffee Shop Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

Note that this project should be run using Python 3.7 (not the latest version)

#### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

On Windows 

check that pip is installed

```bash
py -m pip --version
pip 20.1.1 from F:\Program Files\Python3.7.9\lib\site-packages\pip (python 3.7)
```
set up your virtual environment for the project and create a venv directory 

```bash
py -m venv venv
```

#### PIP Dependencies

Once you have your virtual environment setup and running, navigate to the `/backend` directory and install dependencies by running:

```bash
cd backend
pip install -r requirements.txt
```

This will install all of the required packages we specified within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database. Since we want you to focus on auth, we handle the heavy lift for you in `./src/database/models.py`. We recommend skimming this code first so you know how to interface with the Drink model.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

## Configuring the server

### Run from the backend/src directory

Ensure that you are in the `backend/src` directory before trying to configure and run the server.

```bash
cd src
```

### Configure the logging level

In the `src` and `src/auth` directories review the `logfile.conf` files and amend as necessary.  
You will normally just need to set the logging level by changing the default level of INFO to one of the following:

    CRITICAL
    ERROR
    WARNING
    INFO
    DEBUG

### Set the Authorization Environment Variables

The following authorization variables need to be set up to conform with the settings you set up at Auth0.
For example:

```bash
export AUTH0_DOMAIN="yourdomain.au.auth0.com"
export API_AUDIENCE="yourcoffeeshop"
export ALGORITHM="RS256"
```

## Running the server

Before running up the server ensure that you are in the `./src` directory and that you are working using your created virtual environment.

Each time you open a new terminal session you need to export the environment variables.

To tell Flask which module to run (you only need to do this once per terminal session):

```bash
export FLASK_APP=api.py;
```

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

To stop the server press CTRL+C

## Testing Pre-requisits

The backend uses the Auth0 authentication system to check that the user has the necessary permission to perform the various tasks.

When running the frontend application the logging on and storage of credentials is done by asking the user to log in, which redirects to Auth0 and stores the returned JWT token so you do not need to manually get the JWT tokens.

To test the backend without using the frontend application you will need to get a JWT token manually and either store it as an environment variable for use within your cURL requests or store it in the Postman configuration.

The process to manually get the JWT token and store it is described below.

### To manually get a JWT token

Open a terminal session and set the environment variables to be used to get a JWT token.

```bash
export YOUR_DOMAIN="yourdomain.au.auth0.com"
export YOUR_API_IDENTIFIER="yourcoffeeshop"
export YOUR_CLIENT_ID="DB....MoS"
export YOUR_CALLBACK_URI="http://localhost:8080/login-results"
```

Open a web browser in incognito mode and use the following URL template to log in as a user and get a token.  (Note that you must use incognito mode or the browser will just renew the token without displaying it in the URL bar.)

Use the following template to create the URL required.

```bash
https://{{YOUR_DOMAIN}}/authorize?audience={{YOUR_API_IDENTIFIER}}&response_type=token&client_id={{YOUR_CLIENT_ID}}&redirect_uri={{YOUR_CALLBACK_URI}}
```

For example:

```bash
https://yourdomain.au.auth0.com/authorize?audience=yourcoffeeshop&response_type=token&client_id=DB....MoS&redirect_uri=http://localhost:8080/login-results
```

The browser will attempt to redirect to the redirect_uri (which will not be found) with various parameters which will be displayed in the browser's URL field.  From here you can extract the JWT access token.

```
http://localhost:8080/login-results#access_token=eyJ...PoQ&expires_in=86400&token_type=Bearer
```

If you are testing with cURL you will need to set environment variables to contain the JWT token and your backend test host address, as shown below.

```bash
export TEST_TOKEN="eyJ...PoQ"

export TEST_HOST="http://127.0.0.1:5000"
```

## Check the Server is running
You can now ensure that the backend server is running correctly by trying a simple enquiry.

Using your browser navigate to:

```
http://127.0.0.1:5000/
```

You should see the response:
```
Welcome to the Coffee Shop
```

---
## Base URL
At present this app can only be run locally and is not hosted as a base URL. 

The backend app is hosted at the default, http://127.0.0.1:5000/, which is set as a proxy in the frontend configuration. 

The following API documentation assumes that the base URL has been set as an environment variable as follows:

```bash
export TEST_HOST="http://127.0.0.1:5000"
```

## Errors
Errors are returned as JSON objects in the following format:
```json
{
    "success": false, 
    "error": 400,
    "message": "bad request"
}
```

### Error Index
The following error types can be returned by the API when requests fail:
```
200 Good response
400 Bad Request
404 Not Found
405 Method Not Allowed
422 Unprocessable, usually a databse access error
500 Internal Error
```

## Endpoints

### Endpoints Index
The following endpoints are accepted by the API

    GET    '/'                   # Gets a welcome message
    GET    '/drinks'             # Gets a list of drinks in short format
    GET    '/drinks-detail'      # Gets a list of drinks in long format
    POST   '/drinks'             # Adds a new drink in long format
    PATCH  '/drinks/<drinks_id>' # Amends a drink
    DELETE '/drinks/<drinks_id>' # Deletes a drink

---
### GET '/'
Accesses the home page of the backend which just displays "Welcome to the Coffee Shop".
This is normally just used to check if the web server is responding correctly.

#### curl
```bash
curl ${TEST_HOST}/
```
#### response
```
Welcome to the Coffee Shop
```
#### errors
```
none
```

---
### GET '/drinks'
GET /drinks is a public endpoint returning a list of drinks.

This is used to get a list of drinks in the drink.short() data format
and is used to display the names and colours of the drinks.

#### curl
```bash
curl ${TEST_HOST}/drinks
```
#### response
```json
{
  "drinks":[
    {
      "id":1,
      "recipe":[
        {
          "color":"black",
          "parts":1
        },
        {
          "color":"white",
          "parts":3
        }
      ],
      "title":"White Coffee"
    },
    {
      "id":2,
      "recipe":[
        {
          "color":"black2",
          "parts":2
        },
        {
          "color":"white2",
          "parts":4
        }
      ],
      "title":"White Coffee2"
    }
  ],
  "success":true
}
```
#### errors
```json
{
    "error": 404,
    "message": "404 Not Found: There are no drinks",
    "success": false
}
```

---
### GET '/drinks-detail'
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

#### curl
```bash
curl  ${TEST_HOST}/drinks-detail -H 'Accept: application/json' -H "Authorization: Bearer ${TEST_TOKEN}"

```
#### response
```json
{
  "drinks":[
    {
      "id":1,
      "recipe":[
        {
          "color":"black",
          "name":"coffee",
          "parts":1
        },
        {
          "color":"white",
          "name":"milk",
          "parts":3
        }
      ],
      "title":"White Coffee"
    },
    {
      "id":2,
      "recipe":[
        {
          "color":"black2",
          "name":"coffee2",
          "parts":2
        },
        {
          "color":"white2",
          "name":"milk2",
          "parts":4
        }
      ],
      "title":"White Coffee2"
    }
  ],
  "success":true
}
```
#### errors
```json
{
  "error":401,
  "message":"Authorization header is expected.",
  "success":false
}

{
  "error":401,
  "message":"Token expired.",
  "success":false
}

{
  "error": 404,
  "message": "404 Not Found: There are no drinks",
  "success": false
}
```

---
### POST '/drinks'
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

#### curl to to add a drink
```bash
curl -X POST ${TEST_HOST}/drinks -H 'Accept: application/json' -H "Authorization: Bearer ${TEST_TOKEN}" -H "Cont
ent-Type:application/json" -d '{"title":"Water3","recipe":[{"name":"Water","color":"blue","parts":1}]}'
```
#### response
```json
{
  "drinks":[
    {
      "id":3,
      "recipe":[
        {
          "color":"blue",
          "name":"Water",
          "parts":1
        }
      ],
      "title":"Water3"
    }
  ],
  "success":true
}
```
#### curl to generate an error
The drinks details are not supplied
```bash
curl  -X POST ${TEST_HOST}/drinks -H 'Accept: application/json' -H "Authorization: Bearer ${TEST_TOKEN}"
```
#### error response
```json
{
  "error":400,
  "message":"400 Bad Request: Missing input field(s). (title and recipe are required.)",
  "success":false
}
```
#### other errors
```json
{
    "error": 400,
    "message": "400 Bad Request: Cannot add 'Water3'. That drink already exists in the datbase.",
    "success": false
}```

---
### PATCH '/drinks'

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


#### curl to to amend a drink title
```bash
curl -X PATCH ${TEST_HOST}/drinks/1 -H 'Accept: application/json' -H "Authorization: Bearer ${TEST_TOKEN}" -H "Content-Type:application/json" -d '{"title":"Patched Title Water5"}'
```

#### response
```json
{
  "drinks":[
    {
      "id":3,
      "recipe":[
        {
          "color":"blue",
          "name":"Water",
          "parts":1
        }
      ],
      "title":"Patched Title Water5"
    }
  ],
  "success":true
}
```

#### curl to to amend a drink title and recipe
```bash
curl -X PATCH ${TEST_HOST}/drinks/2 -H 'Accept: application/json' -H "Authorization: Bearer ${TEST_TOKEN}" -H "C 
ontent-Type:application/json" -d '{"title":"Patched Title Water6","recipe":[{"name":"Patched Water","color":"blue","parts":2}]}'
```

#### response
```json
{
  "drinks":[
    {
      "id":2,
      "recipe":[
        {
          "color":"blue",
          "name":"Patched Water",
          "parts":2
        }
      ],
      "title":"Patched Title Water6"
    }
  ],
  "success":true
}
```

#### curl to generate an error
The drinks details are not supplied
```bash
curl  -X POST ${TEST_HOST}/drinks -H 'Accept: application/json' -H "Authorization: Bearer ${TEST_TOKEN}"
```
#### error response
```json
{
  "error":400,
  "message":"400 Bad Request: Missing input field(s). (title and recipe are required.)",
  "success":false
}
```
#### other errors
```json
{
    "error": 400,
    "message": "400 Bad Request: Cannot add 'Water3'. That drink already exists in the datbase.",
    "success": false
}```

---
### DELETE '/drinks<id>'

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

#### curl to to delete a drink
```bash
curl -X DELETE ${TEST_HOST}/drinks/1 -H 'Accept: application/json' -H "Authorization: Bearer ${TEST_TOKEN}"
```

#### response
```json
{
  "delete":1,
  "success":true
}
```

---

## Tasks you will need to do to use the backend

### Setup Auth0

1. Create a new Auth0 Account
1. Select a unique tenant domain
1. Create a new, single page web application
1. Create a new API
    - in API Settings:
        - Enable RBAC
        - Enable Add Permissions in the Access Token
1. Create new API permissions:
    - `get:drinks-detail`
    - `post:drinks`
    - `patch:drinks`
    - `delete:drinks`
1. Create new roles for:
    - Barista
        - can `get:drinks-detail`
    - Manager
        - can perform all actions
1. Register 2 users - assign the Barista role to one and Manager role to the other. 
1. Sign into each account and make note of the JWT. This will be needed for:
    - configuring Postman
    - setting the environment variable if you use cURL for testing

### Set up Postman for testing

Download and install [Postman](https://getpostman.com).
1. Run up Postman.
1. Import the postman collection `backend/udacity-fsnd-udaspicelatte.postman_collection.json`

NOTE!!
You will need to repeat the following process each time that your tokens expire.

1. On Auth0 sign in as the barista and the manager make note of the JWTs.
1. Set the JWT in Postman for the barista
    - Click the collection folder for barista
    - Set the type to Bearer Token
    - Paste the barista JWT into the Token field
    - Click Save (in the top right hand corner) to save the Token and propagate to the child elements)
1. Set the JWT in Postman for the manager (as detailed above)
1. Export the postman collection overwriting  `backend/udacity-fsnd-udaspicelatte.postman_collection.json`

### Implement The Server

There are `@TODO` comments throughout the `./backend/src`. We recommend tackling the files in order and from top to bottom:

1. `./src/auth/auth.py`
2. `./src/api.py`
