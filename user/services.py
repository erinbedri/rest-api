import datetime
import jwt

from core import settings
from . import models


def create_user(user):
    instance = models.User(
        first_name=user["first_name"],
        last_name=user["last_name"],
        email=user["email"]
    )
    if user["password"] is not None:
        instance.set_password(user["password"])

    instance.save()

    return instance


def user_email_selector(email):
    user = models.User.object.filter(email=email).first()

    return user


def create_token(user_id):
    payload = dict(
        id=user_id,
        exp=datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        iat=datetime.datetime.utcnow()
    )
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    return token