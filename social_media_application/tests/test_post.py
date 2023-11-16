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

class TestPosts(unittest.TestCase):
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
        self.post1_id = response.json["id"]

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

    def test_create_post_text(self):
        data = {
            "title": "Test Post 1 by user1",
            "url": "can be blank or anything, final result will be none only",
            "content": "lorem ipsum dolor test content",
            "post_type": "text",
            "tags": "text,hastag,testingtag,user1",
        }
        response = self.client.post(
            "/posts", headers={"Authorization": "Token " + self.token1}, json=data
        )
        self.post1_id = response.json["id"]
        # print(response.json)
        self.assertEqual(response.status_code, 201)

    def test_create_post_image(self):
        data = {
            "title": "Test Post 2 by user1",
            "url": "https://unsplash.com/photos/a-bunch-of-pink-donuts-are-stacked-on-top-of-each-other-obyYZVKwCNI",
            "content": "lorem ipsum dolor test content",
            "post_type": "image",
            "tags": "image,hastag,testingtag,user1",
        }
        response = self.client.post(
            "/posts", headers={"Authorization": "Token " + self.token1}, json=data
        )
        self.post2_id = response.json["id"]
        # print(response.json)
        self.assertEqual(response.status_code, 201)

    def test_create_post_video(self):
        data = {
            "title": "Test Post 3 by user1",
            "url": "https://www.youtube.com/watch?v=CvQ7e6yUtnw&ab_channel=ArjanCodes",
            "content": "lorem ipsum dolor test content",
            "post_type": "video",
            "tags": "video,hastag,testingtag,user1",
        }
        response = self.client.post(
            "/posts", headers={"Authorization": "Token " + self.token1}, json=data
        )
        self.post3_id = response.json["id"]
        # print(response.json)
        self.assertEqual(response.status_code, 201)

    def test_get_all_posts(self):
        response = self.client.get(
            "/posts", headers={"Authorization": "Token " + self.token1}
        )
        # print(response.json)
        self.assertEqual(response.status_code, 200)

    def test_get_post_by_id(self):
        response = self.client.get(
            f"/posts/{self.post1_id}", headers={"Authorization": "Token " + self.token1}
        )
        self.assertEqual(response.status_code, 200)

    def test_update_post_by_id(self):
        data = {"content": "updated content"}
        response = self.client.patch(
            f"/posts/{self.post1_id}",
            headers={"Authorization": "Token " + self.token1},
            json=data,
        )
        # print(response.json)
        self.assertEqual(response.status_code, 200)

    def test_update_post_delete(self):
        response = self.client.delete(
            f"/posts/{self.post1_id}", headers={"Authorization": "Token " + self.token1}
        )
        self.assertEqual(response.status_code, 204)
