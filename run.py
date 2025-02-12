#!/usr/bin/env python
from gevent import monkey
monkey.patch_all()

from app import app, socketio

if __name__ == '__main__':
    socketio.run(app,
                debug=True,
                host='0.0.0.0',
                port=5001,
                use_reloader=True,
                log_output=True,
                allow_unsafe_werkzeug=True) 