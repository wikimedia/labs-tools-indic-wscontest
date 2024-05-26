from pywikisource import WikiSourceApi
import json
import datetime as dt
from pytz import timezone

# Read the contests
with open("contest_data/contests.json", 'r', encoding="utf-8") as file:
    contests = json.load(file)

for k, v in contests.items():
    if (k == "number_of_con") or (v["status"] is False):
        continue
    else:
        con = {}
        user_agent = "IndicWikisourceContest/1.1 (https://example.org/IndicWikisourceContest/;) pywikisource/0.0.5"
        ws = WikiSourceApi(v["project"], user_agent)
        for index in v["index"]:
            try:
                con[index] = {}
                pageList = ws.createdPageList(index.split(':')[1])
                for page in pageList:
                    con[index][page] = {}
                    con[index][page] = ws.pageStatus(page)
            except Exception:
                print("Error in %s contest" % k)
        con["LastUpdate"] = dt.datetime.now(timezone('Asia/Kolkata')).strftime("%A, %d. %B %Y %I:%M%p") + ' IST'

        with open("contest_data/stats/" + k + ".json", 'w', encoding="utf8") as file:
            json.dump(con, file, indent=4, ensure_ascii=False)
