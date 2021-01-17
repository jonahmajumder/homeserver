from http import HTTPStatus
from functools import wraps
from pathlib import Path

from flask import (Flask, 
    request, make_response,
    render_template
)

from secrets import USERNAME, PASSWORD

app = Flask(__name__)

def protected(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth is not None:
            if auth.username == USERNAME and auth.password == PASSWORD:
                return func(*args, **kwargs)

        return make_response(
            '<h2>Incorrect authorization.</h2>',
            HTTPStatus.UNAUTHORIZED.value,
            {'WWW-Authenticate': 'Basic realm="Login required"'}
        )

    return decorated


@app.route('/')
@app.route('/index')
@protected
def index():
    username = request.authorization.username
    return render_template('index.html', title='Index', username=username)

