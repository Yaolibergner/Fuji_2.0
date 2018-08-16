# To initialize socketio to flask application.

from flask import Flask, session, render_template, request
from flask import flash, redirect, url_for, g
from flask_socketio import SocketIO
from flask_socketio import send, emit
from model import connect_to_db, db, User, Message, Chatroom
from model import UserRoom, Translation
from datetime import datetime
from translate import translate_text
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/feedpage')
def feedpage():
    return render_template('feedpage.html')

# Serverside event handler on an unnamed event
# Namespace is to allow multiplex connections
# Broadcast=True allows multiple clients. Which can estiblish chat between
# each other. 

# Check Flask-Socket.io authenticated_only 
# https://flask-socketio.readthedocs.io/en/latest/.

@socketio.on('update', namespace='/chat')
def send_message(msg_evt):
    
    translation = translate_text('zh-CN', msg_evt['value']).translated_text
    print("/////")
    print(translation)
    print("/////")
    # Emit botht the message and the translation.
    emit('response', {'value': msg_evt['value'], 
                      'translation': translation}, broadcast=True)

    # need to add message to database. 


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)