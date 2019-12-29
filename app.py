from flask import Flask, request, redirect, render_template
import os

# Create the app
app = Flask(__name__)
app.secret_key = os.urandom(50)


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


@app.before_request
def force_https():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        return redirect(
            'https://' + request.headers['Host'] + request.headers['X-Original-URI'],
            code=301
        )


if __name__ == '__main__':
    app.run()
