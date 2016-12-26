import json
import re
import requests

from settings import FACEBOOK_TOKEN
from api import api

stm_api = api()


class FacebookHandler:
    que_hora_re = re.compile("a que hora pasa el ([\w\d]+)", re.IGNORECASE)

    def message_received(self, payload):
        line = None
        coordinates = None
        for entry in payload["entry"]:
            for messaging in entry.get("messaging", []):
                sender = messaging["sender"]["id"]
                if messaging.get("message", False):
                    if "text" in messaging["message"]:
                        text = messaging["message"]["text"]
                        match = FacebookHandler.que_hora_re.search(text)
                        if match:
                            line = match.groups()[0]
                    elif "attachments" in messaging["message"]:
                        for attachment in messaging["message"]["attachments"]:
                            if attachment["type"] == "location":
                                coordinates = attachment["payload"]["coordinates"]

                # elif messaging.get("postback", False):
                #     postback = messaging["postback"]["payload"]
        response_message = None
        if line:
            response_message = {
              "recipient": {
                "id": sender
              },
              "message": {
                "text": "Mandame to ubicacion",
                "quick_replies": [
                  {
                    "content_type": "location",
                    "payload": line
                  }
                ]
              }
            }
        elif coordinates:
            line = "57"
            stops = stm_api.search_stops(coordinates["lat"], coordinates["long"])
            print stops
            hour = None
            i = 0
            while not hour and i< len(stops):
                passes = stm_api.get_pases(line, stops[i])
                if passes:
                    hour = passes[0]["horaDesc"]

            if hour:
                response_message = {
                    "recipient": {
                        "id": sender
                    },
                    "message": {
                        "text": hour,
                    }
                }

        if response_message:
            print response_message

            response = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token={}".format(FACEBOOK_TOKEN),
                data=json.dumps(response_message), headers={"Content-Type": "application/json"})
            print response
            print "-" * 50

            print response.content



        # response = requests.get("http://www.montevideo.gub.uy/transporteRest/lineas/{}".format(stop))
# response_message = {
#     "recipient":{
#         "id": sender
#     },
#     "message":{
#         # "text": "Por {} pasan {}".format(parsed["descripcion"], ", ".join([x["descripcion"] for x in parsed["lineas"]]))
#         "attachment": {
#             "type": "template",
#             "payload": {
#                 "template_type": "list",
#                 "top_element_style": "compact",
#                 "elements": [{
#                     "title": x["descripcion"],
#                     "buttons": [{
#                         "type":"postback",
#                         "title":"ver",
#                         "payload": "{}:{}".format(stop, x["codigo"])
#                     }]
#                 } for x in parsed["lineas"][:4]]
#             }
#         }
#     }
# }
