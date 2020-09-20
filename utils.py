import json
from datetime import datetime


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

                    # Create Date Object for easy comparison
                    d1_obj = datetime.strptime(contest["start_date"], '%d-%m-%Y %H:%M')
                    d2_obj = datetime.strptime(contest["end_date"], '%d-%m-%Y %H:%M')
                    d3_obj = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')

                    if user not in proofread and (d1_obj < d3_obj < d2_obj):
                        proofread[user] = [page]
                    elif (d1_obj < d3_obj < d2_obj):
                        proofread[user].append(page)

                if stats[indexPage][page]["validate"] is not None:
                    user = stats[indexPage][page]["validate"]["user"]
                    timestamp = stats[indexPage][page]["validate"]["timestamp"]

                    # Create Date Object for easy comparison
                    d1_obj = datetime.strptime(contest["start_date"], '%d-%m-%Y %H:%M')
                    d2_obj = datetime.strptime(contest["end_date"], '%d-%m-%Y %H:%M')
                    d3_obj = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')

                    if user not in validate and (d1_obj < d3_obj < d2_obj):
                        validate[user] = [page]
                    elif (d1_obj < d3_obj < d2_obj):
                        validate[user].append(page)
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


def get_wikitable(score, point, lastUpdate, contest):
    totalPoints = 0
    totalPR = 0
    totalVD = 0

    wikitable = "Statistics on " + lastUpdate
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
