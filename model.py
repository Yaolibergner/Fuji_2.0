"""Models and database functions for Fuji project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting
# this through the Flask-SQLAlchemy helper library. On this, we can
# find the `session` object, where we do most of our interactions
# (like committing, etc.)

db = SQLAlchemy()


#####################################################################
# Model definitions

class User(db.Model):
    """User of the chatapp."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fname = db.Column(db.String(30), nullable=False)
    lname = db.Column(db.String(30), nullable=True)
    language = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<User user_id={self.user_id} email={self.email}
                    fname={self.fname} language={self.language}>"""

class Message(db.Model):
    """User messages."""

    __tablename__ = "messages"

    message_id = db.Column(db.Integer,
                         autoincrement=True,
                         primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    timestamp = db.Column(db.DateTime)   
    chatroom_id = db.Column(db.Integer, db.ForeignKey('chatrooms.chatroom_id'), nullable=False)
    text = db.Column(db.String(3000))

    user = db.relationship("User",
                           backref=db.backref("messages"))
    chatroom = db.relationship("Chatroom",
                           backref=db.backref("messages"))
    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<message_id={self.message_id}
                   text={self.text} timestamp={self.timestamp} 
                   author_id={self.author_id}
                   chatroom_id={self.chatroom_id}>"""

class Chatroom(db.Model):
    """Chatrooms."""

    __tablename__ = "chatrooms"

    chatroom_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Chatroom chatroom_id={self.chatroom_id}>"        

class UserRoom(db.Model):       
    """Association table for User and Chatroom."""

    # User can be in multiple Chatrooms. Chatrooms can have many users.
    # Build the connection between User and Chatroom tables.
    # Each row will be a pair of one room and one user. 
    __tablename__ = "userrooms"

    userroom_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    chatroom_id = db.Column(db.Integer, db.ForeignKey("chatrooms.chatroom_id"), nullable=False)

    user = db.relationship("User", backref="userrooms")
    chatroom = db.relationship("Chatroom", backref="userrooms")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Userroom userroom_id = {self.userroom_id}
                    user_id={self.user_id}
                    chatroom_id={self.chatroom_id}>"""

class Translation(db.Model):
    """Translated messages."""

    __tablename__ = "translations"

    translation_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.message_id'), nullable=False)
    trans_text = db.Column(db.String(3000), nullable=False)
    language = db.Column(db.String(15), nullable=False)

    message = db.relationship("Message",
                           backref=db.backref("translations"))
   
    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Translation translation_id = {self.translation_id}
                    message_id={self.message_id}
                    trans_text={self.trans_text}
                    language={self.language}>"""

#####################################################################
# Helper functions

# Add example to database for DB and Flask testing. 

def example_data():
    """Adding example to database."""

    chatroom = Chatroom(chatroom_id="1")

    user_1 = User(email="cat@cat.com",
                password="4321",
                fname="cat",
                lname="cat",
                language="en")

    user_2 = User(email="dog@dog.com",
                password="4321",
                fname="dog",
                lname="dog",
                language="zh-CN")

    message = Message(author_id="1", timestamp="08-08-2018",
                      chatroom_id="1", text="What are you doing?")

    db.session.add(chatroom)
    db.session.add(user_1)
    db.session.add(user_2)
    db.session.add(message)
    db.session.commit()

def connect_to_db(app, db_uri='postgresql:///fuji'):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__": # pragma: no cover
    # As a convenience, if we run this module interactively, it will
    # leave you in a state of being able to work with the database
    # directly.

    from fujiserver import app
    connect_to_db(app)
    print("Connected to DB.")
