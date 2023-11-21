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


class TestFeed(unittest.TestCase):
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

        # create post types
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

        # create posts
        data = {
            "title": "Test Post 1 by user1",
            "url": "https://unsplash.com/photos/a-bunch-of-pink-donuts-are-stacked-on-top-of-each-other-obyYZVKwCNI",
            "content": "lorem ipsum dolor test content",
            "post_type": "image",
            "tags": "image,hastag,testingtag,user1",
        }
        response = self.client.post(
            "/posts", headers={"Authorization": "Token " + self.token1}, json=data
        )
        # print(response.json)
        self.post1_id = response.json["id"]

        data = {
            "title": "Test Post 1 by user2",
            "url": "https://unsplash.com/photos/a-bunch-of-pink-donuts-are-stacked-on-top-of-each-other-obyYZVKwCNI",
            "content": "lorem ipsum dolor test content",
            "post_type": "text",
            "tags": "text,hastag,testingtag,user1",
        }
        response = self.client.post(
            "/posts", headers={"Authorization": "Token " + self.token2}, json=data
        )
        self.post2_id = response.json["id"]

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

    def test_get_feed_fail_unauthenticated(self):
        response = self.client.get("/feed")
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in response.json.keys())

    def test_get_feed_self_post_absent(self):
        response = self.client.get(
            "/feed", headers={"Authorization": "Token " + self.token2}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(type(response.json) == list)
        self.assertTrue(self.post2_id not in response.json[0].keys())

    def test_get_feed_no_connection_no_feed(self):
        response = self.client.get(
            "/feed", headers={"Authorization": "Token " + self.token3}
        )
        # print(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(type(response.json) == list)
        self.assertTrue(len(response.json) == 0)
