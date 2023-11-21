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


class TestPostType(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.app_test = app_test
        self.client = app_test.test_client()
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
        self.user_id = response.json["id"]
        self.username = response.json["username"]

        response = self.client.post(
            "/login",
            json={
                "username": self.username,
                "password": "Test@Abcd",
            },
            content_type="application/json",
        )
        self.token = response.json["token"]

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

    def test_create_post_type(self):
        data = {"name": "text"}
        response = self.client.post(
            "/post-types", headers={"Authorization": "Token " + self.token}, json=data
        )
        self.assertEqual(response.status_code, 201)

    def test_create_post_type_fail_no_name(self):
        data = {"name": ""}
        response = self.client.post(
            "/post-types", headers={"Authorization": "Token " + self.token}, json=data
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())

    def test_create_post_type_fail_already_exists(self):
        data = {"name": "text"}
        response = self.client.post(
            "/post-types", headers={"Authorization": "Token " + self.token}, json=data
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())

    def test_create_post_type_fail_unauthenticated(self):
        data = {"name": "text"}
        response = self.client.post("/post-types")
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())

    def test_get_post_type(self):
        response = self.client.get("/post-types")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(type(response.json) == list)
