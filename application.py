import os

from flask import Flask, render_template, session, redirect, request, jsonify
from flask_socketio import SocketIO, emit
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

channels = {"Default":[]}

#Page requires login
def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#Redirect if users are already logged in
def check_login(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is not None:  
            return redirect(f"/index/{session['channel']}")
        # Create default channel    
        session['channel'] = "Default"
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=['GET','POST'])
@check_login
def login():
    if request.method == 'POST':
        name = request.form.get("username")
        if len(name) > 2:
            session['username'] = name
            return redirect(f"/index/{session['channel']}")
        else:
            print("name tooo shortttt")
            return render_template("login.html", Name_too_short=True)
    return render_template("login.html", Name_too_short=False)

#Main page
@app.route("/", methods=['GET','POST'])
@login_required
def main():
    return redirect(f"/index/{session['channel']}")

@app.route("/index/<string:channel>", methods=['GET','POST'])
@login_required
def index(channel):
    if request.method == 'GET':
        session['channel'] = channel
    return render_template("index.html", name=session["username"], channels=channels, channel=channels[channel], channel_name=channel)

@app.route("/add_channel", methods=['POST'])
@login_required
def add_channel():
    global channels
    channel = request.form.get('channel')
    if len(channel) == 0:
        return redirect("/index/" + session['channel'])
    if channel in channels:
        return redirect("/index/" + channel)
    session['channel'] = channel
    channels[channel] = []
    channel = "/index/" + channel
    print(channel)
    return redirect(channel)

@app.route("/clear")
@login_required
def clear():
    global channels
    channels = {"Default":[]}
    session['channel'] = "Default"
    return redirect(f"/index/{session['channel']}")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@socketio.on('new message')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    global channels
    msg = str(json)
    if len(json["message"]) != 0:
        print('received new message: ' + msg)
        channels[session['channel']].append((session["username"],json["message"]))
        socketio.emit('my response', { "username": session["username"], "message": json["message"] })




