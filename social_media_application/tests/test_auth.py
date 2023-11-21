import unittest
import os
from sqlalchemy.sql import text

from social_media_application import create_app, db
from social_media_application.models import User


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


class TestUserOps(unittest.TestCase):
    username = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.app_test = app_test
        cls.client = app_test.test_client()

    @classmethod
    def tearDownClass(cls) -> None:
        with cls.app_test.app_context():
            meta = db.metadata
            for table in reversed(meta.sorted_tables):
                db.session.execute(
                    text(
                        f'TRUNCATE TABLE public."{table.name}" CONTINUE IDENTITY CASCADE;'
                    )
                )
                db.session.commit()

    def test_user_creation(self):
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
        # print(response.json.keys())
        self.assertEqual(response.status_code, 201)
        self.assertTrue("id" in response.json.keys())
        self.assertTrue("profile" in response.json.keys())
        self.assertTrue("username" in response.json.keys())
        self.username = response.json["username"]
        self.assertTrue("email" in response.json.keys())
        with self.app_test.app_context():
            self.assertTrue(User.query.filter_by(username=self.username).first())

    def test_user_creation_fail_username_already_exists(self):
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
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())

    def test_user_creation_fail_email_already_exists(self):
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
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())

    def test_user_login(self):
        response = self.client.post(
            "/login",
            json={
                "username": "testuser1",
                "password": "Test@Abcd",
            },
            content_type="application/json",
        )
        # token = response.json["token"]
        # # print(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("token" in response.json.keys())

    def test_user_login_fail_incorrect_username(self):
        response = self.client.post(
            "/login",
            json={
                "username": "testuser11",
                "password": "Test@Abcd",
            },
            content_type="application/json",
        )
        # token = response.json["token"]
        # print(response.json)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("token" not in response.json.keys())
        self.assertTrue("error" in response.json.keys())

    def test_user_login_fail_incorrect_password(self):
        response = self.client.post(
            "/login",
            json={
                "username": "testuser1",
                "password": "Test@Abcdefg",
            },
            content_type="application/json",
        )
        # token = response.json["token"]
        # print(response.json)
        self.assertTrue("token" not in response.json.keys())
        self.assertTrue("error" in response.json.keys())

    def test_user_logout(self):
        response = self.client.post(
            "/login",
            json={
                "username": "testuser1",
                "password": "Test@Abcd",
            },
            content_type="application/json",
        )
        token = response.json["token"]
        response = self.client.post(
            "/logout", headers={"Authorization": "Token " + token}
        )
        self.assertEqual(response.status_code, 205)

    def test_user_logout_fail_invalid_token(self):
        token = "dhibchbv"
        response = self.client.post(
            "/logout", headers={"Authorization": "Token " + token}
        )
        # print(response.__dict__)
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())

    def test_user_logout_fail_no_token(self):
        response = self.client.post("/logout")
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())
