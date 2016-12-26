import requests
import json
import thread
import sys
import os

from flask import Flask
from flask import request

sys.path.insert(0, os.path.abspath("."))
print sys.path
from channels.facebook import FacebookHandler

app = Flask(__name__)


def call_facebook_handler(*args):
    h = FacebookHandler()
    h.message_received(*args)


@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    print "=" * 50 + "webhook" + "=" * 50
    parsed = json.loads(request.data)
    print parsed
    print "=" * 50 + "webhook" + "=" * 50 + "\n"

    thread.start_new_thread(call_facebook_handler, (parsed,))
    return "OK"

if __name__ == "__main__":
    app.run()
