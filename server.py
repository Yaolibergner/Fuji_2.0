
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
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask import send_from_directory
import sys


# https://flask-bcrypt.readthedocs.io/en/latest/
UPLOAD_FOLDER = '/home/vagrant/src/_FUJI_2.0/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg'])

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
socketio = SocketIO(app)
bcrypt = Bcrypt(app)

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


# Registration page protection.
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if user() is None:
            return redirect(url_for("loginpage"))
        return f(*args, **kwargs)
    return decorated


# Changed register page to addmember. Only changed name for invitation only 
# purpose for now. 
@app.route('/addmember')
@requires_auth
def register_form():
    """Show form for user signup."""

    # A dictionary of language options with it's keys. Key as html option id
    # dict[key] as language options.
    lang_option = {"en": "English", "sv": "Swedish", "zh-CN": "Chinese",
                   "es": "Spanish", "fr": "French", "ru": "Russian",
                   "ar": 'Arabic', "bg": "Bulgarian", "da": "Danish",
                   "fi": "Finnish", "el": "Greek", "hi": "Hindi", "de": "German",
                   "ko": "Korean", "la": "Latin", "pl": "Polish", "pt": "Portuguese"}

    return render_template("addmember.html", lang_option=lang_option)


# Enable user upload files.
def allowed_file(filename):
    """Allow user upload profile picture."""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Changed register page to addmember. Only changed name for invitation only 
# purpose for now. 
@app.route('/addmember', methods=['POST'])
def add_user():
    """Process registration. Add registered user to database."""

    email = request.form.get("email")
    password = request.form.get("password")
    hash_pw = bcrypt.generate_password_hash(password, 10).decode("utf-8")
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    language = request.form.get("language")

    new_user = User(email=email, password=hash_pw, fname=fname,
                    lname=lname, language=language)

    db.session.add(new_user)
    db.session.commit()

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' in request.files:
            file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
            if file.filename != '':
                if file and allowed_file(file.filename):
                    filename = secure_filename(
                        "{}.jpg".format(new_user.user_id))
                    file.save(os.path.join(
                        app.config['UPLOAD_FOLDER'], filename))

    return redirect("/feedpage")


# http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


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
    if not user:
        flash("""You are not a user yet. Please email to request 
              login permission.""")
        return redirect("/")
    hash_pw = user.password
    check_pw = bcrypt.check_password_hash(hash_pw, password)

    if not check_pw:
        flash("Invalid password, please try again!")
        return redirect("/")

    session["user_id"] = user.user_id

    return redirect("/feedpage")


@app.route("/logout")
def logout():
    """User log out."""

    del session["user_id"]
    return redirect("/")


@app.route('/feedpage')
@login_required
def feedpage():
    return render_template('feedpage.html')


# Sqlachemy query response jsonifyable.
def json_response(message):
    """Show query response in a json dict"""
    languages = db.session.query(User.language).distinct()
    translation_dicts = []
    # Converting a list of translations object to a list of translations dict.
    for translation in message.translations:
        translation_dicts.append({
            'language': translation.language,
            'text': translation.trans_text
        })

    return {
        'text': message.text,
        'translations': translation_dicts,
        'author': message.user.fname,
        'author_id': message.author_id
    }


def translation_list(message):
    """Show a list of translations for given message."""
    languages = db.session.query(User.language).distinct()
    # Loop over all existing user distinct languages.
    translation_list = {}
    for language in languages:
        # Languages returns a list of tuples. Language is still a tuple of one
        # element, index language[0] to get the language itself.
        translation_list[language] = translate_text(
            language[0], message).translated_text

    return translation_list

# A messages route with no html, this is to show the jsonified messages.


@app.route('/messages')
def show_messages():
    """Show jsonified messages"""

    messages = Message.query.all()
    # creating a list of dictionary to pass in the json_response function.
    dict_messages = [json_response(message) for message in messages]
    # jsonify only works with list and dictionary.
    return jsonify(dict_messages)


# A languages route with no html, this is to pass in to client.
@app.route('/languages')
def user_languages():
    """Show jsonified user languages."""

    return jsonify({
        'user': user().user_id,
        'language': user().language
    })


# Serverside event handler on an unnamed event
# Namespace is to allow multiplex connections
# Broadcast=True allows multiple clients. Which can estiblish chat between
# each other.


@socketio.on('update', namespace='/chat')
def send_message(msg_evt):
    """Send message to clients."""

    text = msg_evt['value']
    author_id = user().user_id
    timestamp = datetime.now()
    chatroom_id = 1
    new_message = Message(author_id=author_id, timestamp=timestamp,
                          text=text, chatroom_id=chatroom_id)
    db.session.add(new_message)

    # Inserting translation to database.
    for language, translation in translation_list(new_message.text).items():
        message_id = new_message.message_id
        new_translation = Translation(message_id=message_id,
                                      trans_text=translation,
                                      language=language)
        db.session.add(new_translation)
    db.session.commit()

    # Emit both the message and the translation.
    emit('response', json_response(new_message), broadcast=True)


@socketio.on('typing', namespace='/chat')
def is_typing(user_evt):
    """Show user is typing."""

    # if user_evt['value'] != False:
    emit('status', {'value': user_evt['value']}, broadcast=True)


if __name__ == '__main__':  # pragma: no cover
    
    is_production = len(sys.argv) > 1 and sys.argv[1] == "production"
    is_testing = len(sys.argv) > 1 and sys.argv[1] == "testing" 
    if is_testing: 
        print("THIS IS FOR TESTING!")
        app.debug = True
        app.config['UPLOAD_FOLDER'] = '/home/vagrant/src/_FUJI_2.0/uploads_test'
        connect_to_db(app, "postgresql:///testdb")
        db.drop_all()
        db.create_all()
        user_1 = User(email="cat@cat.com",
                  password=bcrypt.generate_password_hash("12345678", 10).decode("utf-8"),
                  fname="Yao",
                  lname="Fun",
                  language="en")
        chatroom_1 = Chatroom(chatroom_id = 1)
        db.session.add(chatroom_1)
        db.session.add(user_1)
        db.session.commit()
        socketio.run(app, host="0.0.0.0", debug=True)
    elif is_production:
        app.config['UPLOAD_FOLDER'] = '/home/ubuntu/Fuji_2.0/uploads'
        connect_to_db(app)
        socketio.run(app, host="0.0.0.0")
    else:
        app.debug = True
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        connect_to_db(app)
        socketio.run(app, host="0.0.0.0", debug=True)
