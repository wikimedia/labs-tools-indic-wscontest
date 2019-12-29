from flask import Flask, request, redirect, render_template, \
    session, url_for
import os
import mwoauth

# Create the app
app = Flask(__name__)

# Load configuration
# export APP_SETTINGS = "config.production" for Production
app.config.from_object(os.environ['APP_SETTINGS'])
app.secret_key = os.urandom(50)

consumer_token = mwoauth.ConsumerToken(
    app.config["CONSUMER_KEY"],
    app.config["CONSUMER_SECRET"]
)
handshaker = mwoauth.Handshaker(app.config["OAUTH_MWURI"], consumer_token)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/contest/', methods=["GET"])
def contest():
    return render_template("contests.html")


@app.route('/contest/create', methods=["GET", "POST"])
def create_contest():
    return render_template("create_contest.html")


@app.route('/contest/<int:id>', methods=["GET"])
def contest_by_id(id):
    return render_template("contest.html")


@app.route('/contest/<int:id>/edit', methods=["GET", "POST"])
def edit_contest(id):
    return render_template("edit_contest.html")


@app.route('/login')
def login():
    redirect_to, request_token = handshaker.initiate()
    keyed_token_name = _str(request_token.key) + '_request_token'
    keyed_next_name = _str(request_token.key) + '_next'
    session[keyed_token_name] = \
        dict(zip(request_token._fields, request_token))

    if 'next' in request.args:
        session[keyed_next_name] = request.args.get('next')
    else:
        session[keyed_next_name] = 'index'

    return redirect(redirect_to)


@app.route('/logout')
def logout():
    session['mwoauth_access_token'] = None
    session['mwoauth_username'] = None
    if 'next' in request.args:
        return redirect(request.args['next'])
    return redirect(url_for('index'))


@app.route('/oauth-callback')
def oauth_callback():
    request_token_key = request.args.get('oauth_token', 'None')
    keyed_token_name = _str(request_token_key) + '_request_token'
    keyed_next_name = _str(request_token_key) + '_next'

    if keyed_token_name not in session:
        err_msg = "OAuth callback failed. Can't find keyed token. Are cookies disabled?"
        return render_template("error.html", msg=err_msg)

    access_token = handshaker.complete(
        mwoauth.RequestToken(**session[keyed_token_name]),
        request.query_string)
    session['mwoauth_access_token'] = \
        dict(zip(access_token._fields, access_token))

    next_url = url_for(session[keyed_next_name])
    del session[keyed_next_name]
    del session[keyed_token_name]

    get_current_user(False)

    return redirect(next_url)


@app.context_processor
def inject_base_variables():
    return {
        "logged": get_current_user() is not None,
        "username": get_current_user()
    }


@app.before_request
def force_https():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        return redirect(
            'https://' + request.headers['Host'] + request.headers['X-Original-URI'],
            code=301
        )


def get_current_user(cached=True):
    if cached:
        return session.get('mwoauth_username')

    # Get user info
    identity = handshaker.identify(
        mwoauth.AccessToken(**session['mwoauth_access_token']))

    # Store user info in session
    session['mwoauth_username'] = identity['username']
    session['mwoauth_useremail'] = identity['email']

    return session['mwoauth_username']


def _str(val):
    """
    Ensures that the val is the default str() type for python2 or 3
    """
    if str == bytes:
        if isinstance(val, str):
            return val
        else:
            return str(val)
    else:
        if isinstance(val, str):
            return val
        else:
            return str(val, 'ascii')


if __name__ == '__main__':
    app.run()
