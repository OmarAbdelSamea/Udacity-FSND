# Coffee Shop Full Stack


Udacity has decided to open a new digitally enabled cafe for students to order drinks, socialize, and study hard. But they need help setting up their menu experience.

# Getting Started

## Backend

### Getting Setup

#### Installing Dependencies

##### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

##### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

##### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

###### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database. Since we want you to focus on auth, we handle the heavy lift for you in `./src/database/models.py`. We recommend skimming this code first so you know how to interface with the Drink model.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

### Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

```bash
export FLASK_APP=api.py;
```

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## Frontend

### Getting Setup

> _tip_: this frontend is designed to work with [Flask-based Backend](../backend). It is recommended you stand up the backend first, test using Postman, and then the frontend should integrate smoothly.

#### Installing Dependencies

##### Installing Node and NPM

This project depends on Nodejs and Node Package Manager (NPM). Before continuing, you must download and install Node (the download includes NPM) from [https://nodejs.com/en/download](https://nodejs.org/en/download/).

##### Installing Ionic Cli

The Ionic Command Line Interface is required to serve and build the frontend. Instructions for installing the CLI  is in the [Ionic Framework Docs](https://ionicframework.com/docs/installation/cli).

##### Installing project dependencies

This project uses NPM to manage software dependencies. NPM Relies on the package.json file located in the `frontend` directory of this repository. After cloning, open your terminal and run:

```bash
npm install
```

>_tip_: **npm i** is shorthand for **npm install**

### Required Tasks

#### Configure Enviornment Variables

Ionic uses a configuration file to manage environment variables. These variables ship with the transpiled software and should not include secrets.

- Open `./src/environments/environments.ts` and ensure each variable reflects the system you stood up for the backend.

### Running Your Frontend in Dev Mode

Ionic ships with a useful development server which detects changes and transpiles as you work. The application is then accessible through the browser on a localhost port. To run the development server, cd into the `frontend` directory and run:

```bash
ionic serve
```

>_tip_: Do not use **ionic serve**  in production. Instead, build Ionic into a build artifact for your desired platforms.
[Checkout the Ionic docs to learn more](https://ionicframework.com/docs/cli/commands/build)

### Key Software Design Relevant to Our Coursework

#### Authentication

The authentication system used for this project is Auth0. `./src/services/auth.service.ts` contains the logic to direct a user to the Auth0 login page, managing the JWT token upon successful callback, and handle setting and retrieving the token from the local store. This token is then consumed by our DrinkService (`./src/services/auth.service.ts`) and passed as an Authorization header when making requests to our backend.

#### Authorization

The Auth0 JWT includes claims for permissions based on the user's role within the Auth0 system. This project makes use of these claims using the `auth.can(permission)` method which checks if particular permissions exist within the JWT permissions claim of the currently logged in user. This method is defined in  `./src/services/auth.service.ts` and is then used to enable and disable buttons in `./src/pages/drink-menu/drink-form/drink-form.html`.

# API

## Error Handling
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
- The API will return three error types when requests fail:
    - 400: Bad Request
    - 401: not authorized
    - 403: forbidden
    - 404: Resource Not Found
    - 405: method not allowed    
    - 422: Not Processable
    - 500: internal server error

## Endpoint Library  
### GET /drinks
- General
    - public endpoint
    - returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks

- Sample: ```curl http://127.0.0.1/drinks```
```
{
  "drinks": [
    {
      "id": 1,
      "recipe": [
        {
          "color": "white",
          "parts": 1
        }
      ],
      "title": "test"
    }
  ],
  "success": true
}
```

### GET /drinks-detail
- General
    - require the 'get:drinks-detail' permission
    - returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks

- Sample: ```curl http://127.0.0.1/drinks-detail```
```
{
  "drinks": [
    {
      "id": 1,
      "recipe": [
        {
          "name": "milk",
          "color": "white",
          "parts": 1
        }
      ],
      "title": "test"
    }
  ],
  "success": true
}
```

### POST /drinks
- General
    - require the 'post:drinks' permission
    - returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the new drink

- Sample: ```curl http://127.0.0.1/drinks -X POST -H "Content-Type: application/json" -d '{"title": "latte", "recipe":[{"name": "milk", "color": "white", "parts":2}, {"name": "coffee", "color": "black", "parts":1}]}' ```
```
{
  "drinks": [
    {
      "id": 2,
      "recipe": [
        {
          "name": "milk",
          "color": "white",
          "parts": 2
        },
        {
          "name": "coffee",
          "color": "black",
          "parts": 1
        }        
      ],
      "title": "latte"
    }
  ],
  "success": true
}
```

### PATCH /drinks/{drink_id}
- General
    - require the 'patch:drinks' permission
    - returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the modfied drink

- Sample: ```curl http://127.0.0.1/drinks/2 -X PATCH -H "Content-Type: application/json" -d '{"title": "cappcino", "recipe":[{"name": "milk", "color": "white", "parts":2}, {"name": "coffee", "color": "black", "parts":1}]}' ```
```
{
  "drinks": [
    {
      "id": 2,
      "recipe": [
        {
          "name": "milk",
          "color": "white",
          "parts": 2
        },
        {
          "name": "coffee",
          "color": "black",
          "parts": 1
        }        
      ],
      "title": "cappcino"
    }
  ],
  "success": true
}
```

### DELETE /drinks/{drink_id}
- General
    - require the 'delete:drinks' permission
    - returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the modfied drink

- Sample: ```curl http://127.0.0.1/drinks/2 -X DELETE' ```
```
{
  "drink_id": 2
  "success": true
}
```

### GET /baristas
- General
    - require the 'get:baristas' permission
    - returns status code 200 and json {"success": True, "data": baristas} where data is the list of baristas

- Sample: ```curl http://127.0.0.1/baristas```
```
{
  "data": [
    {
    "user_id": "auth0|example",
    "picture": "https://example.com/example",
    "name": "john",
    "email": "john.doe@example.com"
    }]   
,
  "success": true
}
```

### POST /baristas/{barista_id}
- General
    - require the 'post:baristas' permission
    - assign the role Barista for the user of the given user_id
    - returns status code 200 and json {"success": True, "barista_id": barista_id} where barista_id is the given user id

- Sample: ```curl http://127.0.0.1/baristas/auth0|example_id -X POST```
```
{
  "barista_id": auth0|example_id 
  "success": true
}
```

### DELETE /baristas/{barista_id}
- General
    - require the 'delete:baristas' permission
    - delete the role Barista for the user of the given user_id
    - returns status code 200 and json {"success": True, "barista_id": barista_id} where barista_id is the given user id

- Sample: ```curl http://127.0.0.1/baristas/auth0|example_id -X DELETE```
```
{
  "barista_id": auth0|example_id 
  "success": true
}
```

### GET /managers
- General
    - require the 'get:managers' permission
    - returns status code 200 and json {"success": True, "data": managers} where data is the list of managers

- Sample: ```curl http://127.0.0.1/managers```
```
{
  "data": [
    {
    "user_id": "auth0|example",
    "picture": "https://example.com/example",
    "name": "omar",
    "email": "omar@example.com"
    }]   
,
  "success": true
}
```

### POST /managers/{manager_id}
- General
    - require the 'post:managers' permission
    - assign the role manager for the user of the given user_id
    - returns status code 200 and json {"success": True, "manager_id": manager_id} where manager_id is the given user id

- Sample: ```curl http://127.0.0.1/managers/auth0|example_id -X POST```
```
{
  "manager_id": auth0|example_id 
  "success": true
}
```

### DELETE /managers/{manager_id}
- General
    - require the 'delete:managers' permission
    - delete the role manager for the user of the given user_id
    - returns status code 200 and json {"success": True, "manager_id": manager_id} where manager_id is the given user id

- Sample: ```curl http://127.0.0.1/managers/auth0|example_id -X DELETE```
```
{
  "manager_id": auth0|example_id 
  "success": true
}
```
## Valid token
### Tokens valid for 7 days starting from 8 of August
- Barista
    - eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlhvRFNOcVM1TGp3NzdnekNLVm9oWSJ9.eyJpc3MiOiJodHRwczovL2Z3ZC1mc25kLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZjJlZTEzMDNhY2QwZTAwM2ExOWRlNzMiLCJhdWQiOiJjb2ZmZWUiLCJpYXQiOjE1OTY5MDgyODgsImV4cCI6MTU5NjkxNTQ4OCwiYXpwIjoiN0Z0VHAzMmRvbkVlNU5lMkdwVkM1MGNkTlRIc2p2OWQiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDpkcmlua3MtZGV0YWlsIl19.dGqHPV8veqXRDZjOB4ezesOOcAcXjkItGlXAlTyvYV8wcB5-PXxwx6nOkM4g3yjK-xKyoQ2Eedf5p9O5NeYM38YksiQ-eCJAysdEoKVgI4Gw_eDRHsszu-qN695bcXsv-_Gi5tR3-zocOkJfHl7_kNtv4u6zHt7wnh6-OxZGyGwsoPKfiQ0ppScl1pWvzAuJbajkyUWYE1APW4_C7wuFQLtR_ZCpirnm3P5gkBbGJgiuJ2zTWcaiRbD6ZxCamrL--zgvAinVlbmP6arcgirweg6jrXA_LXpqPmJ0lpF4fKcsm-uUglMe9xjmXGwO1EIk7TWmdQScAutUm_H2_YMaJA

- Manager 
    - eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlhvRFNOcVM1TGp3NzdnekNLVm9oWSJ9.eyJpc3MiOiJodHRwczovL2Z3ZC1mc25kLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZjJlZTE2OTdkOGE5ZTAwMzc3MTUwMTQiLCJhdWQiOiJjb2ZmZWUiLCJpYXQiOjE1OTY5MDgzNzgsImV4cCI6MTU5NjkxNTU3OCwiYXpwIjoiN0Z0VHAzMmRvbkVlNU5lMkdwVkM1MGNkTlRIc2p2OWQiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTpiYXJpc3RhcyIsImRlbGV0ZTpkcmlua3MiLCJnZXQ6YmFyaXN0YXMiLCJnZXQ6ZHJpbmtzLWRldGFpbCIsInBhdGNoOmRyaW5rcyIsInBvc3Q6YmFyaXN0YXMiLCJwb3N0OmRyaW5rcyJdfQ.KT8o4ehtUhqZIquyAruBtWXC2GfnYka1E3E3LOCOf6e07-PCjdsEcyojLcDDm10o7VqpIAEiPT9GH7tzKzOrhH8zX5pjwCV92-CiOiHa0fW-qMDC_PV1C4mrz1woqs4nucC7cEMJinau3vYmxlMhmydBegsBGOQpYMKVBI0EYlWQiJcVwke4mgQqj4z6eSANUMKS2AJGel78wk3TKCu6M4kCFINEU4Doa6RaOCq9Dio1wZkgB-vJ9jxFyPwHAXoPEAaTwf7O7Wxq0U_LL8jpmonSSr5YPDDbmVCb-QUK-0M1vggC3KqM66U8mfg8TuHS4shgfe7Vp2sb4r2WU8U_1Q

- Adminstrator
    - eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlhvRFNOcVM1TGp3NzdnekNLVm9oWSJ9.eyJpc3MiOiJodHRwczovL2Z3ZC1mc25kLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZjJlZTFmMzdkOGE5ZTAwMzc3MTUwMTYiLCJhdWQiOiJjb2ZmZWUiLCJpYXQiOjE1OTY5MDg0OTgsImV4cCI6MTU5NjkxNTY5OCwiYXpwIjoiN0Z0VHAzMmRvbkVlNU5lMkdwVkM1MGNkTlRIc2p2OWQiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTpiYXJpc3RhcyIsImRlbGV0ZTpkcmlua3MiLCJkZWxldGU6bWFuYWdlcnMiLCJnZXQ6YmFyaXN0YXMiLCJnZXQ6ZHJpbmtzLWRldGFpbCIsImdldDptYW5hZ2VycyIsInBhdGNoOmRyaW5rcyIsInBvc3Q6YmFyaXN0YXMiLCJwb3N0OmRyaW5rcyIsInBvc3Q6bWFuYWdlcnMiXX0.3Cg3ab7cLQMK-OtBZvrGPoagvQunouZ68DWIoIEV_wwpxTdhca_9BTpTcQ-scEyHtTBOqmWaaa1wF7Yki5PscarXG2O4-VgMBo9sU_ecWTD0yIolUu55dRmkcAXtgKzKvgBbNpfdZhMEgVip5t-e3Fh1gcswfFbFXhoHgMJhnOo6riG4ePzW9YbxFsX0qNsHovjw6vhWPv48x3LZPJTwKTZVM6nv9s0h31bxmPADrUDTXZNwwHetF_SxxXx7gdmeX526p8VOCU6pY0eJ9yhXYz4C0yAwpNp82eYocAJZravXyXopZ1BytDWEkkDaAE-ttOFGlx9YLOsNz6P7ldTbsA

## Auth0 Roles

- Barista
    - get:drinks
    - get:drinks-detail

- Manager
    - get:drinks
    - get:drinks-detail
    - post:drinks
    - patch:drinks/{id}
    - delete:drinks/{id}   
    - get:baristas
    - post:baristas
    - delete:baristas

- Adminstrator
    - get:drinks
    - get:drinks-detail
    - post:drinks
    - patch:drinks/{id}
    - delete:drinks/{id}   
    - get:baristas
    - post:baristas
    - delete:baristas
    - get:managers
    - post:managers
    - delete:managers    

## API Reference
- Udacity fullstack nanodegree program final project
- Auth0 management API Docs


## Authors
- Udacity team
- Yours, Omar AbdelSamea