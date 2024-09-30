# Casting Agency
This project represents a casting agency where actors and movies details are maintained.

## Environments
This app can run on the local server, and it is also deployed on `renderer`. 
### Renderer URL of deployed application: https://casting-agency-3r88.onrender.com/



### Run application locally 

For the application to run locally, it is recommended to use `Virtual Environment`.
In order to create a virtual environment, after cloning into this repository run the following command and the virtual environment should be ready:
```bash
python3 -m venv venv
```
After creating the virtual environment, the activation is required. You can activate the virtual environment using the following command:
```bash
source venv/bin/activate
```

#### Installing Pip Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Postgres Dependencies

In the root of this project, there is a file `setup.sh`. This is where the database path is set, in order to connect it to your local database.
Make sure that in your postgres server there is a database called `casting_agency`, in order to create this connection.
The name can be modified, as long as this script matches the database name. 
In the same file, the variables for the Auth0 server are defined.
To set these variables on your os, run the following commands: 
```bash
chmod +x setup.sh
source setup.sh
```
The first command makes file executable and the second should set all variables to the os. To check it, you can run 
```bash
echo ${VARIABLE_NAME}
```

The database contains two models: Actor and Movie, with a many-to-many relation between them.
To make sure that the database contains the tables defined in `models.py`, run:
```bash
flask db upgrade
```

## Running the server

Now that the connection between the database and the application is set, you should be able to run it on the local server. You can do that by running in your terminal:
```bash
python3 app.py
```
The application should start running on a local server, returning `Welcome!`, an endpoint to make sure that the application is running successfully. 


## Auth0
The Auth0 domain is `dev-tool.eu.auth0.com` and API Audience is `drink`

The created roles and their current permissions are: 
1. Casting Assistant
   - `get:actors`
   - `get:movies`
2. Casting Director
   - `get:actors`
   - `get:movies`
   - `post:actors`
   - `patch:actors`
   - `delete:actors`
   - `patch:movies`
3. Executive Producer 
   - `get:actors`
   - `get:movies`
   - `post:actors`
   - `patch:actors`
   - `delete:actors`
   - `patch:movies`
   - `post:movies`
   - `delete:movies`

I generated a JWT token for each role, they can be found in the setUp function from [test_app.py](test_app.py)

## Source Code
### Auth
[auth.py](auth.py) is the file where it is defined the authenticator decorator that is used for all endpoints.
This decorator decrypts the JWT token, checks its validity and user permissions and throws appropriate errors on the contrary.


 - If no authentication token is provided it return `401 Unauthorized`
```json
{
    "code": "authorization_header_missing",
    "description": "Authorization header is expected."
}
```
 - If there is an authentication token, but it does not contain the permission for endpoint it returns `403 Forbidden`
```json
{
    "error": 403,
    "message": "You don't have the permission to access the requested resource.",
    "success": false
}
```


### API
[app.py](app.py) is where the endpoints are defined. As mentioned above, they all require the auth decorator with the specific permissions for each.
There is the endpoint `/` that does not require authentication, it is a test endpoint to make sure that the server is running properly. It does not contain any information from the database as permissions are required for showing them.
I created an endpoint `/login` which redirects to the login page, where I can put the user details that I created in Auth0 with specific roles, and it returns its valid JWT token for simplicity. Therefore this path and the redirects also do not require authentication.

All the other endpoints require authentication. 

#### Error responses
 - `404 Not Found`
```json
{
    "error": 404,
    "message": "Resource not found",
    "success": false
}
```

 - `400 Bad request`
```json
{
    "error": 400,
    "message": "Bad request",
    "success": false
}
```

 - `405 Method not allowed`
```json
{
    "error": 405,
    "message": "Method not allowed.",
    "success": false
}
```
 - `422 Unprocessable`
```json
{
    "error": 422,
    "message": "Unprocessable.",
    "success": false
}
```


#### Endpoints

1. `GET '/actors' and '/movies`
   - Returns all available actors and movies, along with their details
   - Requires `Casting Assistant` role. 
   - If there are no actors or movies, it returns 404
   
   Response Example:
```json
{
    "actors": [
        {
            "age": 33,
            "gender": "Male",
            "id": 1,
            "movie_ids": [],
            "name": "Actor One"
        },
       ...
    ],
    "success": true
},

{
    "movies": [
        {
            "actor_ids": [],
            "id": 1,
            "release_date": "Thu, 28 Sep 2023 12:30:00 GMT",
            "title": "New Movie"
        },
        ...
    ],
    "success": true
}
```
2. `GET '/actors/<id>' and '/movies/<id>`
   - You can search by a specific actor or movie by its id
   - Requires `Casting Assistant` role 
   - If the actor or movie does not exist, it returns 404
   
   Response Example:
```json
{
    "actor": [
        {
            "age": 33,
            "gender": "Male",
            "id": 1,
            "movie_ids": [],
            "name": "Actor One"
        }
    ],
    "success": true
},

{
    "movie": [
        {
            "actor_ids": [],
            "id": 1,
            "release_date": "Thu, 28 Sep 2023 12:30:00 GMT",
            "title": "New Movie"
        }
    ],
    "success": true
}
```

3. `POST '/actors' and '/movies'`
   - You can add an actor or a movie 
   - Requires payload. If payload is not valid, it returns 400
   - Actors require `Casting Director` role
   - Movies require `Executive Producer` role
   
   Payload Example:
```json
//for actors
{
    "name": "New Actor",
    "age": 24,
    "gender": "Female"
}
//for movies
{
    "title": "Movie Title",
    "release_date": "2023-09-28T14:30:00"
}
```
4. `PATCH '/actors/<id>' and '/movies/<id>'`
   - You can edit an actor or a movie details 
   - Requires payload. If payload is not valid, it returns 400
   - Requires `Casting Director` role
   
   Payload Example:
```json
//for actors, /actors/1
{
    "age": 25
}
//for movies, /movies/1
{
    "title": "Titanic"
}
```
   
   Response Example:
```json
{
    "actor": [
        {
            "age": 25,
            "gender": "Male",
            "id": 1,
            "movie_ids": [],
            "name": "Actor One"
        }
    ],
    "success": true
},

{
    "movie": [
        {
            "actor_ids": [],
            "id": 1,
            "release_date": "Thu, 28 Sep 2023 12:30:00 GMT",
            "title": "Titanic"
        }
    ],
    "success": true
}
```



5. `PATCH '/movies/<id>/actors'`
   - You can add actors to a specific movie
   - Requires payload. It must be a list "actor_ids" that contains the ids of the actors that the requester wants to link to the specific movie
   - This endpoint clears the previous actors linked to the movie and links the actors from payload.
   - If payload is not valid, it returns 400
   - Requires `Casting Director` role
   
   Payload Example:
```json
//movies/1/actors
{
    "actor_ids": [1, 2]
}
```
Response example:
```json
{
    "movie": {
        "actor_ids": [
            1, 
            2
        ],
        "id": 1,
        "release_date": "Thu, 28 Sep 2023 12:30:00 GMT",
        "title": "Titanic"
    },
    "success": true
}
```

6. `DELETE '/actors/<id>' and '/movies/<id>''`
   - You can delete an actor or a movie with their ids
   - If the actor or movie is not found, it returns 404
   - Before deleting the actor/movie, it removes the movies/actors linked to them so they do not get removed from the database
   - Actors require `Casting Director` role
   - Movies require `Executive Producer` role
Response example:
```json
//actors/2
{
   "success": true
}
```
   - For example, after deleting actor 2, and you send `GET /movies/1` you can see that actor 1 is still linked to the movie
```json
{
    "movie": {
        "actor_ids": [
            1
        ],
        "id": 1,
        "release_date": "Thu, 28 Sep 2023 12:30:00 GMT",
        "title": "Titanic"
    },
    "success": true
}
```


### Tests
[test_app.py](test_app.py) is the file where all the endpoints are tested.
#### setUp and tearDown function
In this function, the testing application as well as the client are initiated. 
Here you can also find the JWT tokens for all three roles that expire on October 6, 2024.
Also some samples for tests are initiated.
The database is dropped before and after each test so that the tests can be executed anytime without needing to change the ids.

#### Running Tests
The tests can be executed locally from the command line by running 
```bash
python3 test_app.py
```
Careful, by running this command, it drops every actor and movie you added in your local database. 

#### Test Cases
For each endpoint, there are 4 tests: 
- Success 
  - The JWT Token is valid
  - The permission matches
  - The payload (if required) is appropriate
  - The response code and message is as expected
- Bad Request
  - The JWT Token is valid
  - The permission matches
  - The payload (if required) is not appropriate
  - The response code and message is as expected
- Forbidden
  - The JWT Token is valid
  - The permission does not match
  - The response is `403 Forbidden`
- Requires Authentication
  - There is no JWT Token
  - The response is `401 Unauthorised`


### JWT TOKENS
1. Casting Assistant: `eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ii1VUlJNVVg1aVJ5UVFZLUg0WXh6dyJ9.eyJpc3MiOiJodHRwczovL2Rldi10b29sLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NmY4NjkxNjk5ZDMzZjA3MjM4ZDQ1YWIiLCJhdWQiOiJjYXN0aW5nIiwiaWF0IjoxNzI3NjIxOTYzLCJleHAiOjE3MjgyMjY3NjMsImF6cCI6ImVQZ2dMYjJIQ1NzVE9mRHVqY2JNaEllSDdZazFvNmZQIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.YHz9svD52r3hXVMmvEYYUh9xfwIj_rZwTLCW0lOuYzTq5h5mEWkNLR_qJ09rSPNFOqf4S31lovWQ4wmLz2DqwQn-8rsJVu0iSvGISwNBlE9qx1UVHJqgAPg_IblfS5vWjbgRF3mDkdq5kfoablhVRUPmI1QCACFNUhRikbcJeBigwyUBWmhkYR8iSuM7QGXdlVDPq-5BTYhKn-RHPsqF9QW9Zo_4mopl1iWDO0ycBcLX3DiF9cTWbw_U4Otx8TWwtPfunwGoW6ZR0fhqDlkyaXFi4UT0U3PHL8-w388JjUGV7NLGEIHDukGPBaCFk5U6M71Z8nDCAeDgf2EK2SGPQw`
2. Casting Director: `eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ii1VUlJNVVg1aVJ5UVFZLUg0WXh6dyJ9.eyJpc3MiOiJodHRwczovL2Rldi10b29sLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NmY5NTU1NDFkNmM3MDVjN2M0NzVmYWMiLCJhdWQiOiJjYXN0aW5nIiwiaWF0IjoxNzI3NjIyMDI2LCJleHAiOjE3MjgyMjY4MjYsImF6cCI6ImVQZ2dMYjJIQ1NzVE9mRHVqY2JNaEllSDdZazFvNmZQIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.nRs_cu9D7zgxpXwtAIOldfPtfjT3BreD3x7ocrlReCC3HRbTGpW3UzafCNpqcrJ6VoPAgAAOkih9ZirZJdEBNzqD9VLKRRXc8deaE308BF_PhbzGxR0uNAKFQHIy2p1I-vKkhJIsaIKbTV9ItC84FmluBOP-vmgs_GwFw9Mp-07TdFw0WE95nt4ccz6LiJxiBQPImj3bKxtTL92hEEiQWXaA2BgRQi3hDEGbIz-r0PjRUmi11ZOkN1KQEyGHWhYJLJR8iJS8XODImz7y0ZlE2-vGZ22aKnu7Rn0CM1OtqdpOTE9pSa4-wGx9iNp8MqhK0s3AjqC_oFcagOT-EEXRig`
3. Executive Producer: `eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ii1VUlJNVVg1aVJ5UVFZLUg0WXh6dyJ9.eyJpc3MiOiJodHRwczovL2Rldi10b29sLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NmY5NTU4OTllYTk2MzNmZTYyNzkyODkiLCJhdWQiOiJjYXN0aW5nIiwiaWF0IjoxNzI3NjIyMDczLCJleHAiOjE3MjgyMjY4NzMsImF6cCI6ImVQZ2dMYjJIQ1NzVE9mRHVqY2JNaEllSDdZazFvNmZQIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.aR7mi86dsO6U855yFiiTvVlxMnLOQD-MsgmgDKRUnLjlcTeJJNbdm7bmPgMm85X3tAdtjeE62mb7knIa7ocyVjTOXfqnD-pAnNlCptc09juIpaTFFuZTfj0No20ZUFBqaMfPUbpRk141e-r-RhWnA2k53Fu_SOQvqWh5O2B6F9q5OENXYgMJ44o8ZsIVaM2XppcvtweU0XWP5c5vLRt3Gq8xsAmEG7LydpnTty0GtpwQEOASteYFTR9N4qtQVLElH1UwX4UwVgV58KiCs3pYa8IT_u26o8kRTKasJf_l4gNC9RfgE3rMpLT5yW-ql7j0XNAgIJSFYsMTF8w1RmasIw`