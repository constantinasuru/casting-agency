import unittest
import json
from datetime import datetime

from flask import request

from app import create_app, db
from models import Actor, Movie


class TestGetActors(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.assistant_auth_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ii1VUlJNVVg1aVJ5UVFZLUg0WXh6dyJ9.eyJpc3MiOiJodHRwczovL2Rldi10b29sLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NmY4NjkxNjk5ZDMzZjA3MjM4ZDQ1YWIiLCJhdWQiOiJjYXN0aW5nIiwiaWF0IjoxNzI3NjIxOTYzLCJleHAiOjE3MjgyMjY3NjMsImF6cCI6ImVQZ2dMYjJIQ1NzVE9mRHVqY2JNaEllSDdZazFvNmZQIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.YHz9svD52r3hXVMmvEYYUh9xfwIj_rZwTLCW0lOuYzTq5h5mEWkNLR_qJ09rSPNFOqf4S31lovWQ4wmLz2DqwQn-8rsJVu0iSvGISwNBlE9qx1UVHJqgAPg_IblfS5vWjbgRF3mDkdq5kfoablhVRUPmI1QCACFNUhRikbcJeBigwyUBWmhkYR8iSuM7QGXdlVDPq-5BTYhKn-RHPsqF9QW9Zo_4mopl1iWDO0ycBcLX3DiF9cTWbw_U4Otx8TWwtPfunwGoW6ZR0fhqDlkyaXFi4UT0U3PHL8-w388JjUGV7NLGEIHDukGPBaCFk5U6M71Z8nDCAeDgf2EK2SGPQw'
        self.director_auth_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ii1VUlJNVVg1aVJ5UVFZLUg0WXh6dyJ9.eyJpc3MiOiJodHRwczovL2Rldi10b29sLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NmY5NTU1NDFkNmM3MDVjN2M0NzVmYWMiLCJhdWQiOiJjYXN0aW5nIiwiaWF0IjoxNzI3NjIyMDI2LCJleHAiOjE3MjgyMjY4MjYsImF6cCI6ImVQZ2dMYjJIQ1NzVE9mRHVqY2JNaEllSDdZazFvNmZQIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.nRs_cu9D7zgxpXwtAIOldfPtfjT3BreD3x7ocrlReCC3HRbTGpW3UzafCNpqcrJ6VoPAgAAOkih9ZirZJdEBNzqD9VLKRRXc8deaE308BF_PhbzGxR0uNAKFQHIy2p1I-vKkhJIsaIKbTV9ItC84FmluBOP-vmgs_GwFw9Mp-07TdFw0WE95nt4ccz6LiJxiBQPImj3bKxtTL92hEEiQWXaA2BgRQi3hDEGbIz-r0PjRUmi11ZOkN1KQEyGHWhYJLJR8iJS8XODImz7y0ZlE2-vGZ22aKnu7Rn0CM1OtqdpOTE9pSa4-wGx9iNp8MqhK0s3AjqC_oFcagOT-EEXRig'
        self.producer_auth_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ii1VUlJNVVg1aVJ5UVFZLUg0WXh6dyJ9.eyJpc3MiOiJodHRwczovL2Rldi10b29sLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NmY5NTU4OTllYTk2MzNmZTYyNzkyODkiLCJhdWQiOiJjYXN0aW5nIiwiaWF0IjoxNzI3NjIyMDczLCJleHAiOjE3MjgyMjY4NzMsImF6cCI6ImVQZ2dMYjJIQ1NzVE9mRHVqY2JNaEllSDdZazFvNmZQIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.aR7mi86dsO6U855yFiiTvVlxMnLOQD-MsgmgDKRUnLjlcTeJJNbdm7bmPgMm85X3tAdtjeE62mb7knIa7ocyVjTOXfqnD-pAnNlCptc09juIpaTFFuZTfj0No20ZUFBqaMfPUbpRk141e-r-RhWnA2k53Fu_SOQvqWh5O2B6F9q5OENXYgMJ44o8ZsIVaM2XppcvtweU0XWP5c5vLRt3Gq8xsAmEG7LydpnTty0GtpwQEOASteYFTR9N4qtQVLElH1UwX4UwVgV58KiCs3pYa8IT_u26o8kRTKasJf_l4gNC9RfgE3rMpLT5yW-ql7j0XNAgIJSFYsMTF8w1RmasIw'

        db.drop_all()
        db.create_all()

        # Samples for testing
        actor = Actor(name="Actor One", age=30, gender="Male")
        movie = Movie(title="Movie One", release_date=datetime(2024, 9, 29, 15, 30, 45))
        db.session.add(actor)
        db.session.add(movie)
        db.session.commit()

    def tearDown(self):
        """Clean up the database after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_actors_success(self):
        token = self.assistant_auth_token
        response = self.client.get('/actors', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['actors']), 1)

    def test_get_actors_failure(self):
        response = self.client.get('/actors')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['description'], 'Authorization header is expected.')

    def test_get_actor_success(self):
        token = self.assistant_auth_token
        response = self.client.get('/actors/1', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_get_actor_not_found(self):
        token = self.assistant_auth_token
        response = self.client.get('/actors/2', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_actor_no_token(self):
        response = self.client.get('/actors/1')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['description'], 'Authorization header is expected.')

    def test_create_actor_success(self):
        token = self.director_auth_token
        body = {
            "name": "Actor Two",
            "age": 30,
            "gender": "Female",
        }
        response = self.client.post('/actors', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['actor']['name'], 'Actor Two')

    def test_create_actor_bad_request(self):
        token = self.director_auth_token
        body = {
            "name": "Actor Two",
            "age": 30
        }
        response = self.client.post('/actors', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Bad Request')

    def test_create_actor_without_permission(self):
        token = self.assistant_auth_token
        body = {
            "name": "Actor Two",
            "age": 30,
            "gender": "Female"
        }
        response = self.client.post('/actors', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "You don't have the permission to access the requested resource.")

    def test_patch_actor_success(self):
        token = self.director_auth_token
        body = {"age": 31}
        response = self.client.patch('/actors/1', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['actor']['age'], 31)

    def test_patch_actor_not_found(self):
        token = self.director_auth_token
        body = {"age": 31}
        response = self.client.patch('/actors/2', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Resource not found')

    def test_patch_actor_without_permission(self):
        token = self.assistant_auth_token
        body = {
            "age": 33
        }
        response = self.client.patch('/actors/1', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "You don't have the permission to access the requested resource.")

    def test_delete_actor_success(self):
        token = self.director_auth_token
        response = self.client.delete('/actors/1', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_delete_actor_not_found(self):
        token = self.director_auth_token
        response = self.client.delete('/actors/2', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_actor_without_permission(self):
        token = self.assistant_auth_token
        response = self.client.delete('/actors/1', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "You don't have the permission to access the requested resource.")

    def test_get_movies_success(self):
        token = self.assistant_auth_token
        response = self.client.get('/movies', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['movies']), 1)

    def test_get_movies_without_token(self):
        response = self.client.get('/movies')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['description'], 'Authorization header is expected.')

    def test_get_movie_success(self):
        token = self.assistant_auth_token
        response = self.client.get('/movies/1', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_get_movie_not_found(self):
        token = self.assistant_auth_token
        response = self.client.get('/movies/2', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_movie_without_token(self):
        response = self.client.get('/movies/1')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['description'], 'Authorization header is expected.')

    def test_patch_movie_success(self):
        token = self.director_auth_token
        body = {"title": "New Movie"}
        response = self.client.patch('/movies/1', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['movie']['title'], 'New Movie')

    def test_patch_movie_without_permission(self):
        token = self.assistant_auth_token
        body = {"title": "New Movie"}
        response = self.client.patch('/movies/1', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "You don't have the permission to access the requested resource.")

    def test_patch_movie_not_found(self):
        token = self.director_auth_token
        body = {"title": "New Movie"}
        response = self.client.patch('/movies/2', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Resource not found')

    def test_patch_movie_without_token(self):
        body = {"title": "New Movie"}
        response = self.client.patch('/movies/1', json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['description'], 'Authorization header is expected.')

    def test_patch_movie_add_actor_success(self):
        token = self.director_auth_token
        body = {"actor_ids": [1]}
        response = self.client.patch('/movies/1/actors', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['movie']['actor_ids']), 1)

    def test_patch_movie_add_actor_without_permission(self):
        token = self.assistant_auth_token
        body = {"actor_ids": [1]}
        response = self.client.patch('/movies/1/actors', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "You don't have the permission to access the requested resource.")

    def test_patch_movie_add_actors_not_found(self):
        token = self.director_auth_token
        body = {"actor_ids": [1]}
        response = self.client.patch('/movies/2/actors', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Resource not found')

    def test_patch_movie_add_actors_without_token(self):
        body = {"actor_ids": [1]}
        response = self.client.patch('/movies/1/actors', json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['description'], 'Authorization header is expected.')

    def test_create_movie_success(self):
        token = self.producer_auth_token
        body = {
            "title": "New Movie",
            "release_date": "2024-09-29T14:30:45"
        }
        response = self.client.post('/movies', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['movie']['title'], 'New Movie')

    def test_create_movie_bad_request(self):
        token = self.producer_auth_token
        body = {"title": "New Movie"}
        response = self.client.post('/movies', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Bad Request')

    def test_create_movie_without_permission(self):
        token = self.director_auth_token
        body = {
            "title": "New Movie",
            "release_date": "2024-09-29T14:30:45"
        }
        response = self.client.post('/movies', headers={'Authorization': f'Bearer {token}'}, json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "You don't have the permission to access the requested resource.")

    def test_create_movie_no_token(self):
        body = {
            "title": "New Movie",
            "release_date": "2024-09-29T14:30:45"
        }
        response = self.client.post('/movies', json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['description'], 'Authorization header is expected.')

    def test_delete_movie_success(self):
        token = self.producer_auth_token
        response = self.client.delete('/movies/1', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_delete_movie_not_found(self):
        token = self.producer_auth_token
        response = self.client.delete('/movies/2', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Resource not found')

    def test_delete_movie_without_permission(self):
        token = self.director_auth_token
        response = self.client.delete('/movies/1', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "You don't have the permission to access the requested resource.")

    def test_delete_movie_no_token(self):
        response = self.client.delete('/movies/1')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['description'], 'Authorization header is expected.')


if __name__ == '__main__':
    unittest.main()
