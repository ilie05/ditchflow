# init.py
import jwt
from flask import Flask, current_app
from flask_socketio import SocketIO
from auth import auth as auth_blueprint
from flask_login import LoginManager
from main import main as main_blueprint
from contact import contact as contact_blueprint
from database import db
from models import User

app = Flask(__name__)

app.config['SECRET_KEY'] = 'WuLXEWvce8EWr5KEPF'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['JWT_SECRET'] = 'mkFOcbEeBGBHLKiMxM6m'

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


@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    user_entry = None
    if token:
        user_email = jwt.decode(token, current_app.config.get("JWT_SECRET"), algorithms=['HS256'])
        user_entry = User.query.filter_by(email=user_email['email']).first()
    return user_entry


# blueprint for auth routes in our app
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
app.register_blueprint(main_blueprint)

# blueprint for non-auth parts of app
app.register_blueprint(contact_blueprint)

# socketio = SocketIO(app)
# return app, socketio


if __name__ == '__main__':
    # app, socketio = create_app()
    # app.app_context().push()
    app.run(debug=True, port=3000)
    # socketio.run(app, debug=True, port=3000)
