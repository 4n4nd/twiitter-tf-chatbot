import asyncio
import tornado.ioloop
import tornado.web
import tornado
from requests_oauthlib import OAuth1
from peony import PeonyClient

import tf_connect
from configuration import Configuration


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

CURRENT_USER_ID = None

loop = asyncio.get_event_loop()


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


async def getting_started():
    """This is just a demo of an async API call."""
    user = await CLIENT.user
    print("I am @{0}".format(user.screen_name))
    return user


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

    async def post(self):
        message = tornado.escape.json_decode(self.request.body)
        reply_string = (
            "Hi I am fedorafinderbot, send me a picture to to check if there is a red fedora in it."
        )
        print(message)
        print(type(message))
        print(message.keys())
        print(message["message_create"])
        print(message["message_create"]["message_data"])
        print(message["message_create"]["sender_id"])

        print(message["type"])

        if (
            message["type"] == "message_create"  # Check if new message
            and str(message["message_create"]["sender_id"])
            != CURRENT_USER_ID  # Check if its your own message
        ):
            sender_id = str(message["message_create"]["sender_id"])
            print("sender_id: {0}".format(sender_id))
            print("My id: {0}".format(CURRENT_USER_ID))
            message = message["message_create"]["message_data"]
            # Check if an image is present in the message

            # message_data
            if "attachment" in message.keys():
                try:
                    if message["attachment"]["media"]["type"] == "photo":
                        image_url = message["attachment"]["media"]["media_url_https"]

                        # process image and get response from tf model
                        prediction_list = tf_connect.tf_request(TF_SERVER_URL, image_url, AUTH)
                        reply_string = tf_connect.process_output(prediction_list)

                except KeyError:
                    print("No images found")

            # get image url
            # image_url = message.message_create.message_data.attachment.media.media_url_https

            # reply to the message
            reply_json = generate_message_response(sender_id, reply_string)
            response = await CLIENT.api.direct_messages.events.new.post(_json=reply_json)
            print(response)

        self.write(reply_string)


def make_app():
    return tornado.web.Application([(r"/", MainHandler)])


if __name__ == "__main__":
    CURRENT_USER_ID = loop.run_until_complete(getting_started())["id_str"]
    print(CURRENT_USER_ID)
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
