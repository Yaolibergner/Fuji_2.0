# To initialize socketio to flask application.

from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import send, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


# @app.route('/')
# def index():
#     return render_template('test.html')

# Serverside event handler on an unnamed event
# Namespace is to allow multiplex connections
# Broadcast=True allows multiple clients. Which can estiblish chat between
# each other. 

@socketio.on('update', namespace='/test')
def send_message(message):
    emit('response', {'value': message['value']}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)