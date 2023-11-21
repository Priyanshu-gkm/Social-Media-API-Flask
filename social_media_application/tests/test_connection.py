import unittest
import os
from sqlalchemy.sql import text

from social_media_application import create_app, db


def app():
    db_uri = f'postgresql://{os.environ.get("POSTGRES_USERNAME")}:{os.environ.get("PASSWORD")}@{os.environ.get("HOST")}/social_media_test'
    app = create_app(db_uri=db_uri)
    with app.app_context():
        from social_media_application import views
        from social_media_application import models
        from social_media_application import serializers

        db.create_all()
    return app


app_test = app()
client = app_test.test_client()


class TestConnection(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.app_test = app_test
        self.client = app_test.test_client()

        # user 1 data
        response = self.client.post(
            "/register",
            json={
                "username": "testuser1",
                "password": "Test@Abcd",
                "email": "test1@gmail.com",
                "first_name": "test1",
                "last_name": "test1",
                "bio": "test bio",
                "profile_pic": "https://unsplash.com/photos/man-wearing-green-polo-shirt-6anudmpILw4",
            },
            content_type="application/json",
        )
        # print(response.json)
        self.user1_id = response.json["id"]
        self.username1 = response.json["username"]

        response = self.client.post(
            "/login",
            json={
                "username": self.username1,
                "password": "Test@Abcd",
            },
            content_type="application/json",
        )
        self.token1 = response.json["token"]

        # user 2 data
        response = self.client.post(
            "/register",
            json={
                "username": "testuser2",
                "password": "Test@Abcd",
                "email": "test2@gmail.com",
                "first_name": "test2",
                "last_name": "test2",
                "bio": "test bio 2",
                "profile_pic": "https://unsplash.com/photos/man-wearing-green-polo-shirt-6anudmpILw4",
            },
            content_type="application/json",
        )
        self.user2_id = response.json["id"]
        self.username2 = response.json["username"]

        response = self.client.post(
            "/login",
            json={
                "username": self.username2,
                "password": "Test@Abcd",
            },
            content_type="application/json",
        )
        self.token2 = response.json["token"]

        # user 3 data
        response = self.client.post(
            "/register",
            json={
                "username": "testuser3",
                "password": "Test@Abcd",
                "email": "test3@gmail.com",
                "first_name": "test3",
                "last_name": "test3",
                "bio": "test bio 3",
                "profile_pic": "https://unsplash.com/photos/man-wearing-green-polo-shirt-6anudmpILw4",
            },
            content_type="application/json",
        )
        self.user3_id = response.json["id"]
        self.username3 = response.json["username"]

        response = self.client.post(
            "/login",
            json={
                "username": self.username3,
                "password": "Test@Abcd",
            },
            content_type="application/json",
        )
        self.token3 = response.json["token"]

        # create connection
        # send request
        data = {"user": "testuser2"}
        response = self.client.post(
            "/follow-requests",
            headers={"Authorization": "Token " + self.token1},
            json=data,
        )
        # print(response.json)
        self.follow_request_id = response.json["id"]

        # accept request
        data = {"response": "accept"}
        response = self.client.patch(
            f"/follow-requests/{self.follow_request_id}",
            headers={"Authorization": "Token " + self.token2},
            json=data,
        )
        # print(response.json)
        # self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(self) -> None:
        with self.app_test.app_context():
            meta = db.metadata
            for table in reversed(meta.sorted_tables):
                db.session.execute(
                    text(
                        f'TRUNCATE TABLE public."{table.name}" CONTINUE IDENTITY CASCADE;'
                    )
                )
                db.session.commit()

    def test_get_connections(self):
        response = self.client.get(
            "/connections", headers={"Authorization": "Token " + self.token1}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(type(response.json) == list)

    def test_get_connections_fail_unauthenticated(self):
        response = self.client.get("/connections")
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())

    def test_update_connection_delete_fail_unauthenticated(self):
        response = self.client.delete(f"/connections/{self.follow_request_id}")
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())

    def test_update_connection_delete_fail_unauthorised(self):
        response = self.client.delete(
            f"/connections/{self.follow_request_id}",
            headers={"Authorization": "Token " + self.token3},
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue("error" in response.json.keys())

    def test_update_connection_delete_fail_wrong_id(self):
        response = self.client.delete(
            "/connections/some-random-id",
            headers={"Authorization": "Token " + self.token1},
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())

    def test_update_connection_delete_success(self):
        response = self.client.delete(
            f"/connections/{self.follow_request_id}",
            headers={"Authorization": "Token " + self.token1},
        )
        self.assertEqual(response.status_code, 204)
