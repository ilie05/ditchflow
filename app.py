from flask import Flask, current_app
from flask_socketio import SocketIO
from flask_login import LoginManager
from auth import auth as auth_blueprint
from flask_cors import CORS
from flask_migrate import Migrate
import jwt
from database import db
from datetime import timedelta
from main import main as main_blueprint
from contact import contact as contact_blueprint
from sets import sets as sets_blueprint
from models import User
from utils import load_config_settings, prepopulate_db
from sensors_rcv import listen_sensors_thread
from autorun import sending

app = Flask(__name__)

app.config.from_object('config.Config')
load_config_settings(app)
CORS(app)

app.config['SECRET_KEY'] = 'WuLXEWvce8EWr5KEPF'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['JWT_SECRET'] = 'mkFOcbEeBGBHLKiMxM6m'

app.permanent_session_lifetime = timedelta(days=app.config.get("SESSION_DURATION"))

migrate = Migrate(app, db)
db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    user_entry = None
    if token:
        user_email = jwt.decode(token, current_app.config.get("JWT_SECRET"), algorithms=['HS256'])
        user_entry = User.query.filter_by(email=user_email['email']).first()
    return user_entry


app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)
app.register_blueprint(contact_blueprint)
app.register_blueprint(sets_blueprint)

socket_io = SocketIO(app, async_mode='threading')

context = app.app_context()
context.push()

prepopulate_db()

if __name__ == '__main__':
    @app.before_first_request
    def activate_job():
        with context:
            listen_sensors_thread(socket_io)
            sending()


    socket_io.run(app, host='0.0.0.0', debug=True, port=3000)
