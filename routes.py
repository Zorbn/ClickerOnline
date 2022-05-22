from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from encryption import bcrypt
from forms import LoginForm, RegisterForm
from models import Stats, User, db
from producers import default_producers_to_text
from app import MAX_MONEY


routes_bp = Blueprint("routes", __name__, template_folder="templates")


@routes_bp.route("/")
def home():
    top_stats = db.session.query(Stats).order_by(Stats.prestiges)
    top_count = top_stats.count()
    high_scores = []

    for i in range(10):
        if top_count > i:
            username = db.session.get(User, top_stats[i].id).username
            prestiges = top_stats[i].prestiges
            high_scores.append({"username": f"{i+1}. {username}",
                                "prestiges": prestiges})
        else:
            high_scores.append({"username": f"{i+1}. ~",
                                "prestiges": 0})

    return render_template("home.html", high_scores=high_scores)


@routes_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@routes_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("routes.dashboard"))

    return render_template("login.html", form=form)


@routes_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("routes.login"))


@routes_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user_stats = Stats(money=0, prestiges=0,
                               producers=default_producers_to_text())
        new_user = User(username=form.username.data,
                        password=hashed_password, stats=new_user_stats)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("routes.login"))

    return render_template("register.html", form=form)


@routes_bp.context_processor
def prestige_processor():
    def get_can_prestige():
        user_id = current_user.get_id()
        user_stats = db.session.get(Stats, user_id)

        return user_stats.money >= MAX_MONEY

    return dict(get_can_prestige=get_can_prestige)
