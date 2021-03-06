import json
from datetime import datetime
from pytz import timezone

ist_tz = timezone('Asia/Kolkata')
utc_tz = timezone('UTC')


def get_contest_details(id, contest):
    proofread = {}
    validate = {}
    lastUpdate = ""

    try:
        with open("contest_data/stats/" + str(id) + ".json", encoding="utf8") as file:
            stats = json.load(file)

        for indexPage in stats:
            if indexPage == "LastUpdate":
                lastUpdate = stats["LastUpdate"]
                continue
            for page in stats[indexPage]:
                if stats[indexPage][page]["proofread"] is not None:
                    user = stats[indexPage][page]["proofread"]["user"]
                    timestamp = stats[indexPage][page]["proofread"]["timestamp"]
                    rev = stats[indexPage][page]["proofread"].get("revid", None)

                    # Create Date Object for easy comparison
                    d1_obj = ist_tz.localize(datetime.strptime(contest["start_date"], '%d-%m-%Y %H:%M'))
                    d2_obj = ist_tz.localize(datetime.strptime(contest["end_date"], '%d-%m-%Y %H:%M'))
                    d3_obj = utc_tz.localize(datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ'))

                    page_obj = dict(page=page, rev=rev)
                    if user not in proofread and (d1_obj < d3_obj < d2_obj):
                        proofread[user] = [page_obj]
                    elif (d1_obj < d3_obj < d2_obj):
                        proofread[user].append(page_obj)

                if stats[indexPage][page]["validate"] is not None:
                    user = stats[indexPage][page]["validate"]["user"]
                    timestamp = stats[indexPage][page]["validate"]["timestamp"]
                    rev = stats[indexPage][page]["validate"].get("revid", None)

                    # Create Date Object for easy comparison
                    d1_obj = ist_tz.localize(datetime.strptime(contest["start_date"], '%d-%m-%Y %H:%M'))
                    d2_obj = ist_tz.localize(datetime.strptime(contest["end_date"], '%d-%m-%Y %H:%M'))
                    d3_obj = utc_tz.localize(datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ'))

                    page_obj = dict(page=page, rev=rev)
                    if user not in validate and (d1_obj < d3_obj < d2_obj):
                        validate[user] = [page_obj]
                    elif (d1_obj < d3_obj < d2_obj):
                        validate[user].append(page_obj)
    except KeyError:
        pass

    return proofread, validate, lastUpdate


def get_score(proofread, validate):
    # Create empty dict for score
    score = {}
    for usern in proofread.keys():
        score[usern] = {}
        score[usern]["proofread"] = 0
        score[usern]["validate"] = 0

    for usern in validate.keys():
        if usern not in score:
            score[usern] = {}
            score[usern]["proofread"] = 0
            score[usern]["validate"] = 0

    # Fill the score
    for u in proofread:
        score[u]["proofread"] = len(proofread[u])

    for u in validate:
        score[u]["validate"] = len(validate[u])
    return score


def get_wikitable(score, point, lastUpdate, contest, id):
    totalPoints = 0
    totalPR = 0
    totalVD = 0

    wikitable = "{{Clickable button 2|Statistics on " + lastUpdate + \
        "|class=mw-ui-progressive|url=https://tools.wmflabs.org/indic-wscontest/contest/" + str(id) + "}}\n\n"
    wikitable += "'''Proofread point''': " + str(contest["p_points"]) + \
        " and '''Validate point''': " + str(contest["v_points"])
    wikitable += """
{| class="wikitable sortable"
|-
! User
! Proofread
! Validate
! Total Points"""
    for user in score:
        u_pts = (score[user]["proofread"] * point["p"]) + (score[user]["validate"] * point["v"])
        totalPoints += u_pts
        totalPR += score[user]['proofread']
        totalVD += score[user]['validate']

        wikitable += """\n|-
|%s || %d || %d || %d """ % (
            "[[s:" + contest["project"] + ":User:" + user + "|" + user + "]]",
            score[user]['proofread'],
            score[user]['validate'],
            u_pts
        )

    wikitable += "\n|}\n\n"

    wikitable += """{| class="wikitable"
! <br> !! Index page !! Participant !! Proofread !! Validations !! Points
|-
| Total || %d || %d || %d || %d || %d
|}""" % (len(contest["index"]), len(score.keys()), totalPR, totalVD, totalPoints)

    return wikitable


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
