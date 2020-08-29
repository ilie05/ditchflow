import jwt
from flask import Flask, current_app
from flask_socketio import SocketIO
from auth import auth as auth_blueprint
from flask_login import LoginManager
from datetime import timedelta
from main import main as main_blueprint
from contact import contact as contact_blueprint
from database import db
from models import User
from sensors_rcv import listen_sensors_thread
from flask_sse import sse

app = Flask(__name__)

app.config.from_object('config.Config')

# app.config["REDIS_URL"] = "redis://localhost"

app.config['SECRET_KEY'] = 'WuLXEWvce8EWr5KEPF'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['JWT_SECRET'] = 'mkFOcbEeBGBHLKiMxM6m'

app.permanent_session_lifetime = timedelta(days=app.config.get("SESSION_DURATION"))

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

if __name__ == '__main__':
    context = app.app_context()
    context.push()


    # @app.route('/send')
    # def send_sse_message():
    #     sse.publish({"message": "Hello!"}, type='greeting')
    #     return "Message sent!"


    @app.before_first_request
    def activate_job():
        with context:
            listen_sensors_thread(context)


    app.run(host='0.0.0.0', debug=True, port=3000, threaded=True)
