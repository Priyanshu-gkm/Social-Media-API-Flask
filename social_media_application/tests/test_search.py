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


class TestSearch(unittest.TestCase):
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
        self.post1_title = response.json["title"]
        self.post1_tags = "hastag"

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

    def test_search_user(self):
        url = f"/search?username={self.username1}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("id" in response.json.keys())

    def test_search_user_fail(self):
        url = f"/search?username=absgvd"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())

    def test_search_post(self):
        url = f"/search?post={self.post1_title}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(type(response.json) == list)

    def test_search_post_fail(self):
        url = f"/search?post=jvbifh db vhjib bivb"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())

    def test_search_tag(self):
        url = f"/search?tag={self.post1_tags}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(type(response.json) == list)

    def test_search_tag_fail(self):
        url = f"/search?tag=unknowntag"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json.keys())
