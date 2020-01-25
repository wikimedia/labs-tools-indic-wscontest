Indic Wikisource Contest
=======================

* Production tool: https://tools.wmflabs.org/indic-wscontest/
* Issue tracker: https://phabricator.wikimedia.org/tag/indic-techcom/
* Discussion: [https://meta.wikimedia.org/wiki/Indic-TechCom/Tools/Indic_Wikisource_Contest](https://meta.wikimedia.org/wiki/Indic-TechCom/Tools/Indic_Wikisource_Contest)

## Installation

1. Clone repo: `git clone "https://gerrit.wikimedia.org/r/labs/tools/indic-wscontest"`
2. `cd indic-wscontest`
3. `python3 -m venv venv`
4. `source venv/bin/activate`
5. `pip install -r requirements.txt`
6. `export APP_SETTINGS=config.local`
7. Run: `python3 app.py`
8. Open http://127.0.0.1:5000/

edit `config.py` to add test CONSUMER_KEY and CONSUMER_SECRET for OAuth.

## License

This is Free Software, released under the MIT License.
