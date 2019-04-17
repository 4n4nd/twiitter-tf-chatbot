import tornado.ioloop
import tornado.web
import tornado
import json


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

    async def post(self):
        data = self.request.body
        print(data)
        print(type(data))

        data = tornado.escape.json_decode(self.request.body)
        print(data)
        print(type(data))

        # data = tornado.escape.json_decode(self.request.body)
        # data = tornado.escape.to_unicode(self.request.body)
        # print(data)
        # print(self.request.body)
        # json_data = json.loads(self.get_argument("data"))
        # print(type(self.get_argument("data")))
        # print(json_data)
        self.write("OK")


def make_app():
    return tornado.web.Application([(r"/", MainHandler)])


if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
