import unittest
import os
from sqlalchemy.sql import text

from social_media_application import create_app, db
from social_media_application.models import Notification, Connection


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


class TestFollowRequest(unittest.TestCase):
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

        # create user 3
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

        # create connection user 1 and user 3
        with self.app_test.app_context():
            connection = Connection(
                sender=self.user1_id, receiver=self.user3_id, accepted=True
            )
            db.session.add(connection)
            db.session.commit()

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

    def test_follow_request_send_fail_unauthenticated(self):
        data = {"user": "testuser2"}
        response = self.client.post("/follow-requests", json=data)
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())
        self.assertTrue("Unauthenticated" in response.json.values())

    def test_follow_request_send_fail_invalid_username(self):
        data = {"user": "some-random-user-name"}
        response = self.client.post(
            "/follow-requests",
            json=data,
            headers={"Authorization": "Token " + self.token1},
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())
        self.assertTrue("unknown username " + data["user"] in response.json.values())

    def test_follow_request_send_fail_self(self):
        data = {"user": self.username1}
        response = self.client.post(
            "/follow-requests",
            json=data,
            headers={"Authorization": "Token " + self.token1},
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())
        self.assertTrue(
            "You can't send follow request to yourself" in response.json.values()
        )

    def test_follow_request_send_1_2_and_notifications(self):
        data = {"user": self.username2}
        response = self.client.post(
            "/follow-requests",
            headers={"Authorization": "Token " + self.token1},
            json=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("id" in response.json.keys())

        with self.app_test.app_context():
            connection = Connection.query.filter_by(
                sender=self.user1_id, receiver=self.user2_id
            ).first()  # request sent
            notification = Notification.query.filter_by(
                user=self.user2_id
            ).first()  # notification made

            self.assertTrue(connection.id)
            self.assertTrue(notification.id)

    def test_follow_request_send_1_3_existing_connection(self):
        data = {"user": self.username3}
        response = self.client.post(
            "/follow-requests",
            headers={"Authorization": "Token " + self.token1},
            json=data,
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())


class TestFollowRequestResponse(unittest.TestCase):
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

        # create user 3
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

        # create connections
        with self.app_test.app_context():
            connection1 = Connection(sender=self.user1_id, receiver=self.user3_id)
            connection2 = Connection(sender=self.user1_id, receiver=self.user2_id)
            connection3 = Connection(
                sender=self.user2_id, receiver=self.user3_id, accepted=True
            )
            db.session.add(connection1)
            db.session.add(connection2)
            db.session.add(connection3)
            db.session.commit()
            self.connection1_id = connection1.id
            self.connection2_id = connection2.id
            self.connection3_id = connection3.id

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

    def test_follow_request_update_fail_unauthenticated(self):
        data = {"response": "accept"}
        response = self.client.patch(
            f"/follow-requests/{self.connection1_id}", json=data
        )
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())
        self.assertTrue("Unauthenticated" in response.json.values())

    def test_follow_request_update_fail_unauthorized(self):
        data = {"response": "accept"}
        response = self.client.patch(
            f"/follow-requests/{self.connection1_id}",
            headers={"Authorization": "Token " + self.token2},
            json=data,
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue("error" in response.json.keys())
        self.assertTrue(
            "you are not authorised for this follow request!" in response.json.values()
        )

    def test_follow_request_get_fail_unauthenticated(self):
        response = self.client.patch(f"/follow-requests/{self.connection1_id}")
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())

    def test_follow_request_respond_fail_unauthenticated(self):
        data = {"response": "accept"}
        response = self.client.patch(
            f"/follow-requests/{self.connection1_id}",
            json=data,
        )
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())

    def test_follow_request_respond_fail_unauthorized(self):
        data = {"response": "accept"}
        response = self.client.patch(
            f"/follow-requests/{self.connection1_id}",
            headers={"Authorization": "Token " + self.token2},
            json=data,
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue("error" in response.json.keys())

    def test_follow_request_respond_fail_already_accepted(self):
        data = {"response": "accept"}
        response = self.client.patch(
            f"/follow-requests/{self.connection3_id}",
            headers={"Authorization": "Token " + self.token3},
            json=data,
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())
        self.assertTrue("you cant do this, already accepted!" in response.json.values())

    def test_follow_request_respond_accept_success(self):
        data = {"response": "accept"}
        response = self.client.patch(
            f"/follow-requests/{self.connection1_id}",
            headers={"Authorization": "Token " + self.token3},
            json=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("id" in response.json.keys())
        self.assertTrue("accepted" in response.json.keys())
        self.assertEqual(response.json["accepted"], True)

        with self.app_test.app_context():
            connection = Connection.query.filter_by(
                sender=self.user1_id, receiver=self.user3_id
            ).first()  # request sent
            notification = Notification.query.filter_by(
                user=self.user1_id
            ).first()  # notification made

            self.assertTrue(connection.id)
            self.assertTrue(notification.id)

    def test_follow_request_respond_reject_success(self):
        data = {"response": "reject"}
        response = self.client.patch(
            f"/follow-requests/{self.connection2_id}",
            headers={"Authorization": "Token " + self.token2},
            json=data,
        )
        self.assertEqual(response.status_code, 200)

        with self.app_test.app_context():
            connection = Connection.query.filter_by(
                sender=self.user1_id, receiver=self.user2_id
            ).first()  # request deleted
            notification = Notification.query.filter_by(
                user=self.user1_id
            ).first()  # notification made

            self.assertIsNone(connection)
            self.assertTrue(notification.id)
