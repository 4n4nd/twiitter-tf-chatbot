import asyncio
import peony
from peony import PeonyClient
from requests_oauthlib import OAuth1

import hmac, base64, hashlib
import json
from flask import Flask, request
from http import HTTPStatus

import tf_connect
from configuration import Configuration

app = Flask(__name__)

# create the client using the api keys
CLIENT = PeonyClient(
    consumer_key=Configuration.CONSUMER_KEY,
    consumer_secret=Configuration.CONSUMER_SECRET,
    access_token=Configuration.ACCESS_TOKEN,
    access_token_secret=Configuration.ACCESS_TOKEN_SECRET,
)
AUTH = OAuth1(
    Configuration.CONSUMER_KEY,
    Configuration.CONSUMER_SECRET,
    Configuration.ACCESS_TOKEN,
    Configuration.ACCESS_TOKEN_SECRET,
)

TF_SERVER_URL = Configuration.TF_SERVER_URL


def generate_message_response(to_user_id, message_string: str):
    message_response = {
        "event": {
            "type": "message_create",
            "message_create": {
                "target": {"recipient_id": to_user_id},
                "message_data": {"text": "{0}".format(str(message_string))},
            },
        }
    }
    return message_response


@app.route("/")
def default_page():

    return "default page"


@app.route("/webhook", methods=["GET"])
def twitter_crc_validation():

    crc = request.args["crc_token"]

    validation = hmac.new(
        key=bytes(Configuration.CONSUMER_SECRET, "utf-8"),
        msg=bytes(crc, "utf-8"),
        digestmod=hashlib.sha256,
    )
    digested = base64.b64encode(validation.digest())
    response = {"response_token": "sha256=" + format(str(digested)[2:-1])}
    print("responding to CRC call")
    return json.dumps(response)


async def getting_started():
    """This is just a demo of an async API call."""
    user = await CLIENT.user
    print("I am @{0}".format(user.screen_name))
    return str(user.screen_name)


def process_message(message):
    print(message)
    if message.type == "message_create":  # validate message here !!!! Add better validation
        print("new message received")
        # if message valid

        # get image url
        image_url = message.message_create.message_data.attachment.media.media_url_https

        # process image and get response from tf model
        prediction_list = tf_connect.tf_request(TF_SERVER_URL, image_url, AUTH)
        reply_string = tf_connect.process_output(prediction_list)

        # reply to the message
        reply_json = generate_message_response(message.message_create.sender_id, reply_string)
        response = CLIENT.api.direct_messages.events.new.post(_json=reply_json)
        return response
    return "Invalid message"


@app.route("/webhook", methods=["POST"])
def twitter_event_received():
    event_json = request.get_json()
    if "direct_message_events" in event_json.keys():
        for message in event_json.direct_message_events:
            process_message(message)

    return ("", HTTPStatus.OK)


# async def process_dms():
#     while True:
#         if UNANSWERED_MESSAGE_LIST:
#             local_messages = UNANSWERED_MESSAGE_LIST
#             async for message in local_messages:
#                 # process message
#                 image_url = message.message_create.message_data.attachment.media.media_url_https
#                 pil_image = image_downloader(image_url, auth=AUTH)
#
#                 reply_string = "default message"
#
#                 # reply to message
#                 reply_to = message.message_create.sender_id
#                 # message destroy request to twitter
#                 # Don't forget to delete the reply that was just sent
#
#                 # delete message
#                 del UNANSWERED_MESSAGE_LIST[UNANSWERED_MESSAGE_LIST.index(message)]
#
#                 pass
#             pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
    # loop.run_until_complete(getting_started())
