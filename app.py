from flask import Flask, request, redirect, render_template, \
    session, url_for, abort, jsonify
import os
import json
import mwoauth
from datetime import datetime
from pytz import timezone
from utils import get_contest_details, get_score, get_wikitable, _str

# Create the app
app = Flask(__name__)

# Load configuration
# export APP_SETTINGS=config.production for Production
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
    with open("contest_data/contests.json", encoding="utf8") as file:
        contest = json.load(file)
    return jsonify(contest)


@app.route('/api/contest/create', methods=["POST"])
def create_contest():
    if get_current_user() is not None:
        con = {}
        number_of_con = 0
        req = request.form

        con["name"] = req["c_name"]
        con["project"] = req["c_project"]
        con["start_date"] = req["start_date"]
        con["end_date"] = req["end_date"]
        con["p_points"] = req["p_proofread"]
        con["v_points"] = req["p_validate"]
        con["createdon"] = datetime.now(timezone('Asia/Kolkata')).strftime("%d-%m-%Y, %H:%M")
        con["createdby"] = get_current_user()
        con["status"] = True

        # Split into list
        con["index"] = req.get("index_pages").split('\r\n')
        con["admin"] = req.get("c_admin").split('\r\n')

        with open("contest_data/contests.json", encoding="utf8") as file:
            contest = json.load(file)
            number_of_con = int(contest["number_of_con"]) + 1

        # Increament number_of_con and create key
        contest["number_of_con"] = number_of_con
        contest[number_of_con] = {}
        contest[number_of_con] = con

        # Rewrite contests.json with new contest
        with open("contest_data/contests.json", 'w', encoding="utf8") as file:
            json.dump(contest, file, indent=4, ensure_ascii=False)

        # Create empty JSON for stats of contest
        c_no = str(number_of_con)
        with open("contest_data/stats/" + c_no + ".json", 'w', encoding="utf8") as file:
            json.dump({}, file, indent=4, ensure_ascii=False)

        return jsonify({
            "status": "success",
            "contestno": c_no
        })


@app.route('/api/contest/<int:id>', methods=["GET"])
def contest_by_id(id):
    with open("contest_data/contests.json", encoding="utf8") as file:
        contest = json.load(file)

    contest = contest.get(str(id))

    # Remove whitespace around the admins
    contest["admin"] = [i.strip() for i in contest["admin"]]

    # Check whether contest is exist or not
    if contest is None:
        abort(404)

    proofread, validate, lastUpdate = get_contest_details(id, contest)

    score = get_score(proofread, validate)

    point = {
        "p": int(contest["p_points"]),
        "v": int(contest["v_points"])
    }

    wikitable = get_wikitable(score, point, lastUpdate, contest, id)
    return jsonify({
        "data": contest,
        "proofread": proofread,
        "validate": validate,
        "lastUpdate": lastUpdate,
        "score": score,
        "point": point,
        "wikitable": wikitable
    })


@app.route('/api/contest/<int:id>/edit', methods=["POST"])
def edit_contest(id):
    if get_current_user() is not None:
        req = request.form

        contest[str(id)]["name"] = req["c_name"]
        contest[str(id)]["project"] = req["c_project"]
        contest[str(id)]["start_date"] = req["start_date"]
        contest[str(id)]["end_date"] = req["end_date"]
        contest[str(id)]["p_points"] = req["p_proofread"]
        contest[str(id)]["v_points"] = req["p_validate"]

        if 'c_status' in req:
            contest[str(id)]["status"] = True

            # Change update status
            with open("contest_data/stats/" + str(id) + ".json", 'r+', encoding="utf8") as file:
                c_details = json.load(file)
                c_details["LastUpdate"] = "Contest Updated, Stats will generate soon."
                file.seek(0)
                json.dump(c_details, file, indent=4, ensure_ascii=False)
                file.truncate()
        else:
            contest[str(id)]["status"] = False

        # Split into list
        contest[str(id)]["index"] = req.get("index_pages").split('\r\n')
        contest[str(id)]["admin"] = req.get("c_admin").split('\r\n')

        # Rewrite contests.json with edit contest
        with open("contest_data/contests.json", 'w', encoding="utf8") as file:
            json.dump(contest, file, indent=4, ensure_ascii=False)

        return jsonify({
            "status": "success"
        })


@app.route('/api/graph', methods=["GET"])
def graph():
    projects = request.args.get("c")
    if projects is not None:
        projects = projects.split("|")
        projects_data = {}

        # Open the contests data
        with open("contest_data/contests.json", encoding="utf8") as file:
            contests = json.load(file)

        # Iterate project from request
        for i in projects:
            projects_data[i] = {}
            projects_data[i]["proofread"], projects_data[i]["validate"], \
                projects_data[i]["lastUpdate"] = get_contest_details(i, contests.get(str(i)))

        result = {}
        for k, v in projects_data.items():
            result[k] = {}
            result[k]["project"] = contests[k]["project"]
            result[k]["index_page"] = len(contests[k]["index"])
            result[k]["user_profread"] = sum([len(i) for i in projects_data[k]["proofread"].values()])
            result[k]["user_validate"] = sum([len(i) for i in projects_data[k]["validate"].values()])

            # Unique users of proofread and validation
            total_user = list(projects_data[k]["proofread"].keys()) + list(projects_data[k]["validate"].keys())
            result[k]["total_user"] = len(set(total_user))
        return jsonify(result)

    return jsonify({
        "error": "Param c id required."
    }), 400


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


@app.template_filter('dateformat')
def timectime(s):
    d = datetime.strptime(s, '%d-%m-%Y, %H:%M')
    return datetime.timestamp(d)


if __name__ == '__main__':
    app.run()
