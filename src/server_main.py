#!/usr/bin/env python
import os
import time
import random
from threading import Lock
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit

async_mode = None

# This variable keeps a track of the number of events that has occur
event_counter = 0
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('on_click')
def kill_server():
    global event_counter

    funny_statements = ['The Server Died',
                        'You Eliminated the server',
                        'What the HELL !! You killed the server']

    session['receive_count'] = session.get('receive_count', 0) + 1

    # Increment counter by 1 cause an event occurred
    event_counter += 1

    # Raise an event with a random choice of statement from the list
    emit('response', {'data': random.choice(funny_statements)})

    # The event takes sometime to be raised .. to avoid UNDEF behaviour this is
    # added
    time.sleep(1)

    # if a event is occurred and handle close the server
    if event_counter >= 1:
        os._exit(0)


@socketio.on('connect')
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


if __name__ == '__main__':
    socketio.run(app, debug=True)
