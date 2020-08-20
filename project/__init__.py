# init.py
from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from auth import auth as auth_blueprint
from main import main as main_blueprint
from contact import contact as contact_blueprint
from database import db
from models import User

socketio = None


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'WuLXEWvce8EWr5KEPF'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    app.register_blueprint(main_blueprint)

    # blueprint for non-auth parts of app
    app.register_blueprint(contact_blueprint)

    # global socketio
    # socketio = SocketIO(app)
    # return app, socketio

    return app


if __name__ == '__main__':
    # app, socketio = create_app()
    app = create_app()
    # app.app_context().push()
    app.run(debug=True, port=3000)
    # socketio.run(app, debug=True, port=3000)
