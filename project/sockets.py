from . import socketio


@socketio.on('event1')
def handle_message(message):
    print('received message: ' + message)


socketio.emit('newnumber', {'number': 25}, namespace='/test')
