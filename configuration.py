import os


class Configuration:

    CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY", "")
    CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET", "")
    ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
    ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
    TF_SERVER_URL = os.getenv("TF_SERVER_URL", "")
