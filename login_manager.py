from flask import redirect, request
from flask_login import LoginManager

from models import User


login_manager = LoginManager()
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized_user():
    return redirect("/login?next=" + request.path)
