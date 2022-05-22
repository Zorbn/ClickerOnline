from app import app

from login_manager import login_manager
from encryption import bcrypt

from routes import routes_bp
from models import db
from events import socketio


if __name__ == "__main__":
    app.register_blueprint(routes_bp)
    db.app = app
    db.init_app(app)
    db.create_all()  # Create all tables that don't exist yet

    login_manager.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)

    socketio.run(app, debug=True)
