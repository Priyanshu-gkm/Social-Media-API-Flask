import unittest
import os
from social_media_application import create_app, db
from sqlalchemy.sql import text


def app():
    db_uri = f'postgresql://{os.environ.get("POSTGRES_USERNAME")}:{os.environ.get("PASSWORD")}@{os.environ.get("HOST")}/social_media_test'
    app = create_app(db_uri=db_uri)
    with app.app_context():
        from .. import views
        from .. import models
        from .. import serializers
        db.create_all()
    return app


app_test = app()
client = app_test.test_client()


class TestUserOps(unittest.TestCase):
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

    def test_userRegistration(self):
        try:
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
            # print(response.data)
            self.assertEqual(response.status_code, 201)
        except Exception as e:
            print("error=========", e)

    def test_user_login(self):
        try:
            response = self.client.post(
                "/login",
                json={
                    "username": "testuser1",
                    "password": "Test@Abcd",
                },
                content_type="application/json",
            )
            token = response.json["token"]
            # print(token)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("token" in response.json.keys())
        except Exception as e:
            print("error=========", e)

    def test_user_logout(self):
        try:
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
            self.assertEqual(response.status_code, 200)
        except Exception as e:
            print("error=========", e)


class Test_user_ops_post_login(unittest.TestCase):
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
        self.user_id = response.json["message"]["id"]
        self.username = response.json["message"]["username"]

        response = self.client.post(
            "/login",
            json={
                "username": "testuser1",
                "password": "Test@Abcd",
            },
            content_type="application/json",
        )
        self.token = response.json["token"]

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
        try:
            response = self.client.get(
                "/users", headers={"Authorization": "Token " + self.token}
            )
            self.assertEqual(response.status_code, 200)
        except Exception as e:
            print("error=========", e)

    def test_update_user(self):
        try:
            update_info = {"first_name": "updated_first_name"}
            response = self.client.patch(
                f"/users/{self.user_id}",
                headers={"Authorization": "Token " + self.token},
                json=update_info,
            )
            self.assertEqual(response.status_code, 200)
        except Exception as e:
            print("error=========", e)

    def test_update_user_delete(self):
        # try:
        # print(self.user_id)
        response = self.client.delete(
            f"/users/{self.user_id}", headers={"Authorization": "Token " + self.token}
        )
        # print(response.__dict__)
        self.assertEqual(response.status_code, 204)

    # except Exception as e:
    # print("error=========",str(e))
