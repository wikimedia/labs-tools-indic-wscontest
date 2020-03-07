from pywikisource import WikiSourceApi
import json

# Read the contests
with open("contest_data/contests.json", 'r', encoding="utf-8") as file:
    contests = json.load(file)

for k, v in contests.items():
    if k == "number_of_con":
        continue
    else:
        con = {}
        ws = WikiSourceApi(v["project"])
        for index in v["index"]:
            try:
                con[index] = {}
                pageList = ws.createdPageList(index.split(':')[1])
                for page in pageList:
                    con[index][page] = {}
                    con[index][page] = ws.pageStatus(page)
            except Exception:
                print("Error in %d contest" % k)

        with open("contest_data/stats/" + k + ".json", 'w', encoding="utf8") as file:
            json.dump(con, file, indent=4, ensure_ascii=False)
