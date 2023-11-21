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


class TestUser(unittest.TestCase):
    @classmethod
    def setUpClass(self):
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

        response = self.client.post(
            "/register",
            json={
                "username": "testuser2",
                "password": "Test@Abcd",
                "email": "test2@gmail.com",
                "first_name": "test2",
                "last_name": "test2",
                "bio": "test bio",
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

    @classmethod
    def tearDownClass(cls):
        with cls.app_test.app_context():
            meta = db.metadata
            for table in reversed(meta.sorted_tables):
                db.session.execute(
                    text(
                        f'TRUNCATE TABLE public."{table.name}" CONTINUE IDENTITY CASCADE;'
                    )
                )
                db.session.commit()

    def test_get_all_users(self):
        response = self.client.get(
            "/users", headers={"Authorization": "Token " + self.token1}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(type(response.json) == list)
        self.assertTrue(len(response.json) > 0)

    def test_get_all_users_fail_unauthenticated(self):
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())

    def test_get_user_by_id(self):
        response = self.client.get(
            f"/users/{self.user1_id}", headers={"Authorization": "Token " + self.token2}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) > 0)
        self.assertTrue("username" in response.json.keys())

    def test_get_user_by_id_fail_invalid_id(self):
        response = self.client.get(
            "/users/sone-random-id", headers={"Authorization": "Token " + self.token1}
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("username" not in response.json.keys())

    def test_get_user_by_id_fail_unauthenticated(self):
        response = self.client.get("/users/some-random-id")
        self.assertEqual(response.status_code, 401)
        self.assertTrue("username" not in response.json.keys())

    def test_update_user(self):
        update_info = {"first_name": "updated_first_name"}
        response = self.client.patch(
            f"/users/{self.user1_id}",
            headers={"Authorization": "Token " + self.token1},
            json=update_info,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["profile"]["first_name"], "updated_first_name")

    def test_update_user_fail_others_id(self):
        update_info = {"first_name": "updated_first_name"}
        response = self.client.patch(
            f"/users/{self.user2_id}",
            headers={"Authorization": "Token " + self.token1},
            json=update_info,
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue("error" in response.json.keys())

    def test_update_user_fail_invalid_attribute(self):
        update_info = {"fname": "updated_first_name"}
        response = self.client.patch(
            f"/users/{self.user2_id}",
            headers={"Authorization": "Token " + self.token2},
            json=update_info,
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())

    def test_update_user_fail_unauthenticated(self):
        update_info = {"first_name": "updated_first_name"}
        response = self.client.patch(
            f"/users/{self.user2_id}",
            json=update_info,
        )
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())

    def test_update_user_delete(self):
        response = self.client.delete(
            f"/users/{self.user2_id}", headers={"Authorization": "Token " + self.token2}
        )
        # print(response.__dict__)
        self.assertEqual(response.status_code, 204)
        with self.app_test.app_context():
            self.assertTrue(
                User.query.filter_by(username=self.username2).first().archive
            )

    def test_update_user_delete_fail_other_id(self):
        response = self.client.delete(
            f"/users/{self.user2_id}", headers={"Authorization": "Token " + self.token1}
        )
        # print(response.__dict__)
        self.assertEqual(response.status_code, 403)
        self.assertTrue("error" in response.json.keys())

    def test_update_user_delete_unauthenticated(self):
        response = self.client.delete(f"/users/{self.user2_id}")
        # print(response.__dict__)
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())
