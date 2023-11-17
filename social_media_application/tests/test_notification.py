import unittest
import os
from sqlalchemy.sql import text

from social_media_application import create_app, db
from social_media_application.models import Notification


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


class TestNotification(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.app_test = app_test
        self.client = app_test.test_client()

        # create user 1
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

        # create user 2
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

        # create notification
        with self.app_test.app_context():
            self.notification_1 = Notification(user=self.user1_id, msg="random msg 1")
            self.notification_2 = Notification(user=self.user1_id, msg="random msg 2")
            self.notification_3 = Notification(user=self.user1_id, msg="random msg 3")

            db.session.add(self.notification_1)
            db.session.add(self.notification_2)
            db.session.add(self.notification_3)

            db.session.commit()
            self.notification1_id = self.notification_1.id
            self.notification2_id = self.notification_2.id
            self.notification3_id = self.notification_3.id

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

    def test_notification_fail_unauthenticated(self):
        response = self.client.get("/notifications")
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())

    def test_notification_success_empty(self):
        response = self.client.get(
            "/notifications", headers={"Authorization": "Token " + self.token2}
        )
        # print(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(type(response.json) == list)
        self.assertTrue(len(response.json) == 0)

    def test_notification_success(self):
        response = self.client.get(
            "/notifications", headers={"Authorization": "Token " + self.token1}
        )
        # print(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(type(response.json) == list)
        self.assertTrue(len(response.json) != 0)

    def test_notification_update_fail_unauthorized(self):
        response = self.client.patch(
            f"/notifications/{self.notification1_id}",
            headers={"Authorization": "Token " + self.token2},
        )
        # print(response.json)
        self.assertEqual(response.status_code, 403)
        self.assertTrue("error" in response.json.keys())

    def test_notification_update_fail_unauthenticated(self):
        response = self.client.patch(f"/notifications/{self.notification1_id}")
        # print(response.json)
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())

    def test_notification_update_read(self):
        response = self.client.patch(
            f"/notifications/{self.notification1_id}",
            headers={"Authorization": "Token " + self.token1},
        )
        # print(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("message" in response.json.keys())

    def test_notification_update_read_all(self):
        response = self.client.patch(
            "/notifications", headers={"Authorization": "Token " + self.token1}
        )
        # print(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("message" in response.json.keys())

    def test_notification_update_read_all_unauthenticated(self):
        response = self.client.patch("/notifications")
        # print(response.json)
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())
