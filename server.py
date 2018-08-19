# To initialize socketio to flask application.

from flask import Flask, session, render_template, request
from flask import flash, redirect, url_for, g
from flask import jsonify
from flask_socketio import SocketIO
from flask_socketio import send, emit
from model import connect_to_db, db, User, Message, Chatroom
from model import UserRoom, Translation
from datetime import datetime
from translate import translate_text
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
socketio = SocketIO(app)

# Define globle user function. Call this function in the future g.user usage.
# Memoization: to memorize the result of the query, in case the query is called
# more then once. 
def user():
    # Check if g.user already called, then not query the database again.
    if not hasattr(g, 'user'):
        if session.get("user_id"):
            user = User.query.filter_by(user_id=session["user_id"]).first()
        else: 
            user = None      
        g.user = user   
    return g.user

#  Add a login_required decorator. This is to protect feedpage not being showed 
#  if user not logged in.
#  http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if user() is None:
            return redirect(url_for("loginpage", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register')
def register_form():
    """Show form for user signup."""

    # A dictionary of language options with it's keys. Key as html option id
    # dict[key] as language options. 
    lang_option = {"en": "English", "sv": "Swedish", "zh-CN": "Chinese", 
               "es": "Spanish", "fr": "French", "ru": "Russian"}


    return render_template("register.html", lang_option=lang_option)


@app.route('/register', methods=['POST'])
def add_user():
    """Process registration. Add registered user to database."""

    email = request.form.get("email")
    password = request.form.get("password")
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    language = request.form.get("language")

    new_user = User(email=email, password=password,fname=fname,
                    lname=lname,language=language)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/")

@app.route("/")
def loginpage():
    """Provide login form."""

    return render_template("loginpage.html")

@app.route("/login", methods=['POST'])
def logininfo():
    """Login for the chatpage."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()
    # import pdb; pdb.set_trace()
    if not user:
        return redirect("/register")

    if user.password != password:
        flash('Invalid password, please try again!')
        return redirect("/")

    session["user_id"] = user.user_id

    return redirect("/feedpage")

@app.route("/logout")
def logout():
    """User log out."""

    del session["user_id"]
    flash("You are logged out, see you soon.")
    return redirect("/")

@app.route('/feedpage')
@login_required
def feedpage():
    return render_template('feedpage.html')

# Serverside event handler on an unnamed event
# Namespace is to allow multiplex connections
# Broadcast=True allows multiple clients. Which can estiblish chat between
# each other. 

# Check Flask-Socket.io authenticated_only 
# https://flask-socketio.readthedocs.io/en/latest/.

# Sqlachemy query response jsonifyable.
def json_response(message):
    """Show query response in a json dict"""

    return {'text': message.text,
            # only return the first language translation. Need to loop for 
            # all languages. 
            'translation': 'nihao',
            #message.translations[0].trans_text,
            'author': message.user.fname,  
            # 'timestamp': message.timestamp
            }

@app.route("/messages")
def show_messages():
    """Show messages on feedpage"""

    messages = Message.query.all()

    for message in messages:
        # message.translation gives list of objects. All the translation for the 
        # language. Here assgin it to one trans_text based on user's language
        # selection. 
        message.translation = Translation.query.filter_by(language=user().language,   
                                            message_id=message.message_id).first()
    # creating a list of dictionary to pass in the json_response function.
    dict_messages= [json_response(message) for message in messages]
    return jsonify(dict_messages)


@socketio.on('update', namespace='/chat')
def send_message(msg_evt):

    translation = translate_text('zh-CN', msg_evt['value']).translated_text

    text = msg_evt['value']
    author_id = user().user_id
    timestamp = datetime.now()
    chatroom_id = 1
    new_message = Message(author_id=author_id, timestamp=timestamp,
                          text=text, chatroom_id=chatroom_id)
    db.session.add(new_message)
    db.session.commit()
    # Emit botht the message and the translation.
    emit('response', json_response(new_message), broadcast=True)

    # Later, need to use session to define what translation to send back.



    # languages = db.session.query(User.language).distinct()
    # # Loop over all existing user distinct languages. And translate the original message
    # # to each language. Add translated messages to database.
    # for language in languages:
    #     # languages returns a list of tuples. language is still a tuple of one element.
    #     # index language[0] to fix it. 
    #     trans_text = translate_text(language[0], message).translated_text
    #     message_id = new_message.message_id
    #     new_translation = Translation(message_id=message_id, trans_text=trans_text,
    #                                   language=language)
    #     db.session.add(new_translation)
    
    # db.session.commit()

if __name__ == '__main__': # pragma: no cover

    app.debug = True

    connect_to_db(app)
    socketio.run(app, host="0.0.0.0", debug=True)




