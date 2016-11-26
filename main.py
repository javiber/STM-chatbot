from flask import Flask
from flask import request
import json
import requests

app = Flask(__name__)

@app.route("/")
def hello():
    response = requests.get("http://www.montevideo.gub.uy/transporteRest/lineas/3029")
    parsed = json.loads(response.content)

    return "Por {} pasan {}".format(parsed["descripcion"], ", ".join([x["descripcion"] for x in parsed["lineas"]]))


@app.route("/times", methods=['GET', 'POST'])
def times():
    print "=" * 50
    print "****times****"
    print request.data
    print "-" * 50
    print request.args
    print "=" * 50 + "\n"
    return ""


@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    parsed = json.loads(request.data)
    print "=" * 50
    print "****webhook*****"
    print parsed

    text = None
    postback = None
    for entry in parsed["entry"]:
        for messaging in entry.get("messaging", []):
            sender = messaging["sender"]["id"]
            if messaging.get("message", False):
                text = messaging["message"]["text"]
            elif messaging.get("postback", False):
                postback = messaging["postback"]["payload"]

    if text:
        stop = text
        response = requests.get("http://www.montevideo.gub.uy/transporteRest/lineas/{}".format(stop))
        parsed = json.loads(response.content)
        response_message = {
            "recipient":{
                "id": sender
            },
            "message":{
                # "text": "Por {} pasan {}".format(parsed["descripcion"], ", ".join([x["descripcion"] for x in parsed["lineas"]]))
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "list",
                        "top_element_style": "compact",
                        "elements": [{
                            "title": x["descripcion"],
                            "buttons": [{
                                "type":"postback",
    					        "title":"ver",
    					        "payload": "{}:{}".format(stop, x["codigo"])
                            }]
                        } for x in parsed["lineas"][:4]]
                    }
                }
            }
        }
    elif postback:
        response = requests.get("http://www.montevideo.gub.uy/transporteRest/pasadas/{}/HABIL/{}".format(*postback.split(":")))
        parsed = json.loads(response.content)
        response_message = {
            "recipient":{
                "id": sender
            },
            "message":{
                "text": parsed[0]["horaDesc"]
            }
        }

    print response_message

    response = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=EAAZAw7ABxMRIBAGXnaIoZB4nFXhm1tZAhRjZA9J6RtM99EGHS2CabAlxscOX4UmCrjQ76bGoF7OZAxWpUvhzRTUiRRt182VKZBlqdC1soTeZAkUFniPZBGII8k8pZB8hsR9QacwMS8MMxV383GIrSt1WZC7DjXUNtIZAeaS4CaWINupdwZDZD",
        data=json.dumps(response_message), headers={"Content-Type": "application/json"})
    print response
    print "-" * 50

    print response.content
    print "=" * 50 + "\n"

    return "OK"

if __name__ == "__main__":
    app.run()
