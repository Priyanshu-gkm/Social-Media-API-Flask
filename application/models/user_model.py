from flask import current_app as app
from application.models.blacklist_token import BlacklistToken
from .. import db, ma
import uuid
from sqlalchemy.dialects.postgresql import UUID
from passlib.hash import bcrypt
from datetime import timedelta as td  # Time managing
from datetime import datetime as dt
from marshmallow import fields
import jwt  # jwt token


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )  # Private id
    username = db.Column(db.String(32), index=True, nullable=False)
    password_hash = db.Column(
        db.String(64), nullable=False
    )  # Hashed password for better security
    email = db.Column(db.String(50), unique=True, nullable=False)
    archive = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, email, password, username):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.hash(password)

    def hash_password(self, password):
        """
        Returns encrypted password from real-one
        :param password: str
        :return: str
        """
        self.password_hash = bcrypt.hash(password)

    def verify_password(self, password):
        """
        Returns true when password is correct
        :param password: str
        :return: boolean
        """
        return bcrypt.verify(password, self.password_hash)

    def generate_auth_token(self, expires_in=td(days=1)):
        """
        Returns jwt token for jwt-authentication
        :param expires_in: timedelta
        :return: str
        """
        try:
            payload = {
                "exp": dt.utcnow() + expires_in,
                "iat": dt.utcnow(),
                "username": self.username,
            }
            return jwt.encode(payload, app.config.get("SECRET_KEY"), algorithm="HS256")
        except Exception as e:
            return e

    @staticmethod
    def verify_auth_token(token):
        """
        Returns true when token is correct
        :param token: str
        :return: boolean
        """
        try:
            is_blacklisted_token = BlacklistToken.check_blacklist(token)
            if is_blacklisted_token:
                return "Token expired. Please log in again."
            else:
                payload = jwt.decode(
                    token, app.config["SECRET_KEY"], algorithms=["HS256"]
                )
                return payload["username"]
        except jwt.ExpiredSignatureError:
            return "Signature expired. Please log in again."
        except jwt.InvalidTokenError:
            return "Invalid token. Please log in again."

    def __repr__(self):
        return f"<User {self.username}>"


class Profile(db.Model):
    __tablename__ = "profile"
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    bio = db.Column(db.String(255))
    profile_pic = db.Column(db.String(500), default=None)
    archive = db.Column(db.Boolean, default=False, nullable=False)


class ProfileSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "bio", "profile_pic")


profile_schema = ProfileSchema()
profiles_schema = ProfileSchema(many=True)


# User Schema
class UserSchema(ma.Schema):
    profile = fields.Method("get_profile")

    def get_profile(self, obj):
        return profile_schema.dump(Profile.query.filter_by(user=obj.id).first())

    class Meta:
        fields = ("id", "username", "email", "profile")


user_schema = UserSchema()
users_schema = UserSchema(many=True)
