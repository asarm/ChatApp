import os
from collections import deque

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


messages = {}
channels = []
users = []

@app.route("/login",methods=['post','get'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        users.append(username)
        session['username'] = username
        print(f"username is {session.get('username') }")
        session.permanent = True
        return redirect('/')
    return render_template('login.html')


@app.route("/logout", methods=['POST', 'GET'])
def logout():
    session.clear()
    print(users)
    return render_template('login.html')


@app.route("/", methods=['POST', 'GET'])
def home():
    print(messages)
    if session.get('username') != None:
        username = session['username']
        return render_template('home.html',channel_list=channels,username=username,users=users)
    else:
        return render_template('login.html')

@app.route("/channel/create", methods=['POST', 'GET'])
def create_channel():
    if request.method == 'POST':
        channel_name = request.form.get('channel_name')
        if channel_name in channels:
            print(f'error, room {channel_name} is exist')
        else:
            channels.append(channel_name)
            messages[channel_name] = []

    if session.get('username') != None:
        username = session['username']
        return render_template('create_channel.html',username=username,channels=channels)
    else:
        return render_template('create_channel.html',channels=channels)


@app.route("/channel/<channel_name>", methods=['POST', 'GET'])
def channel(channel_name):
    global current_channel
    current_channel = channel_name
    if session.get('username') != None:
        username = session['username']
        if len(messages[channel_name])>=100:
            messages[channel_name].pop(0)
        return render_template('chat.html',username=username,messages=messages[channel_name])
    else:
        return render_template('login.html')


@app.route("/channels")
def show_channels():
    if session.get('username') != None:
        username = session['username']
        return render_template('channels.html', channel_list=channels, username=username,users=users)
    else:
        return render_template('login.html')


@socketio.on("joined")
def join():
    join_room(current_channel)

    emit('status', {
        'userJoined': current_channel,
        'channel': current_channel,
        'message': session.get('username') + ' has joined',
        'username': session.get('username')
            },
         room=current_channel
        )

@socketio.on('send message')
def send_msg(message, timestamp):
    """ Receive message with timestamp and broadcast on the channel """
    # Broadcast only to users on the same channel.
    if len(messages[current_channel]) > 100:
        # Pop the oldest message
        messages[current_channel].pop(-1)

    messages[current_channel].append([timestamp, session.get('username'), message])
    emit('announce message', {
        'user': session.get('username'),
        'timestamp': timestamp,
        'message': message},
         room=current_channel)

