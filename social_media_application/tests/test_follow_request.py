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


class TestFollow(unittest.TestCase):
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
        self.user1_id = response.json["message"]["id"]
        self.username1 = response.json["message"]["username"]

        response = self.client.post(
            "/login",
            json={
                "username": "testuser1",
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
                "bio": "test bio 2",
                "profile_pic": "https://unsplash.com/photos/man-wearing-green-polo-shirt-6anudmpILw4",
            },
            content_type="application/json",
        )
        self.user2_id = response.json["message"]["id"]
        self.username2 = response.json["message"]["username"]

        response = self.client.post(
            "/login",
            json={
                "username": "testuser2",
                "password": "Test@Abcd",
            },
            content_type="application/json",
        )
        self.token2 = response.json["token"]

        response = self.client.post(
            "/post-types",
            headers={"Authorization": "Token " + self.token1},
            json={"name": "text"},
        )
        response = self.client.post(
            "/post-types",
            headers={"Authorization": "Token " + self.token1},
            json={"name": "image"},
        )
        response = self.client.post(
            "/post-types",
            headers={"Authorization": "Token " + self.token1},
            json={"name": "video"},
        )

        data = {
            "title": "Test Post n by user1",
            "url": "https://unsplash.com/photos/a-bunch-of-pink-donuts-are-stacked-on-top-of-each-other-obyYZVKwCNI",
            "content": "lorem ipsum dolor test content",
            "post_type": "image",
            "tags": "image,hastag,testingtag,user1",
        }
        response = self.client.post(
            "/posts", headers={"Authorization": "Token " + self.token1}, json=data
        )
        self.post1_id = response.json["data"]["id"]

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

    def test_follow_request_send_1_2_and_notifications(self):
        data = {"user": "testuser2"}
        response = self.client.post(
            "/follow-requests", headers={"Authorization": "Token " + self.token1}, json=data
        )
        # print(response.__dict__)
        self.assertEqual(response.status_code, 201)

        response = self.client.get(
            "/notifications", headers={"Authorization": "Token " + self.token2}
        )
        # print(response.json)
        self.assertEqual(response.status_code, 200)

    def test_get_follow_requests_accept(self):
        response = self.client.get(
            "/follow-requests", headers={"Authorization": "Token " + self.token2}
        )
        # print(response.json)
        self.assertEqual(response.status_code, 200)

        follow_request_id = response.json["message"][0]["id"]
        data = {"response": "accept"}
        response = self.client.patch(
            f"/follow-requests/{follow_request_id}",
            headers={"Authorization": "Token " + self.token2},
            json=data,
        )
        # print(response.json)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "/notifications", headers={"Authorization": "Token " + self.token1}
        )
        # print(response.json)
        self.assertEqual(response.status_code, 200)

    def test_get_follow_requests_accept_feed(self):
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
        username3 = response.json["message"]["username"]

        response = self.client.post(
            "/login",
            json={
                "username": username3,
                "password": "Test@Abcd",
            },
            content_type="application/json",
        )
        token3 = response.json["token"]
        data = {
            "title": "Test Post 1 by user3",
            "url": "https://unsplash.com/photos/a-bunch-of-pink-donuts-are-stacked-on-top-of-each-other-obyYZVKwCNI",
            "content": "lorem ipsum dolor test content",
            "post_type": "image",
            "tags": "image,hastag,testingtag,user3",
        }
        response = self.client.post(
            "/posts", headers={"Authorization": "Token " + token3}, json=data
        )
        self.post1_id = response.json["data"]["id"]

        response = self.client.get(
            "/posts", headers={"Authorization": "Token " + self.token2}
        )
        # print("all the posts")
        # print(response.json)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "/connections", headers={"Authorization": "Token " + self.token2}
        )
        # print("connections")
        # print(response.json)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "/feed", headers={"Authorization": "Token " + self.token2}
        )
        # print("user feed")
        # print(response.json)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "/connections", headers={"Authorization": "Token " + self.token2}
        )
        self.assertEqual(response.status_code, 200)
        follow_request_id = response.json["message"][0]["id"]
        response = self.client.delete(
            f"/follow-requests/{follow_request_id}",
            headers={"Authorization": "Token " + self.token1},
        )
        # print(response.__dict__)
        self.assertEqual(response.status_code, 204)
