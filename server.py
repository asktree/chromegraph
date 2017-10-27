import tornado.ioloop
import tornado.web
import pymongo
from tornado import gen
from urllib.parse import urlparse


"""
Server executable with associated handler and functions for handling requests
"""

class CGManager():
    def __init__(self):
        self.last_active = ""

        client = pymongo.MongoClient("localhost")
        try:
            # The ismaster command is cheap and does not require auth.
            client.admin.command('ismaster')
            print("Mongo connected")
        except pymongo.errors.ConnectionFailure:
            print("Mongo not available")
        db = client.chromegraph
        self.coll = db.agrippa

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, cgm):
        self.cgm = cgm

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, Content-Type")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self):
        self.set_status(204)
        self.finish()

    def get(self):
        # obviously this needs to be integrated into the page code
        self.write(repr(list(self.cgm.coll.find())))

    @gen.coroutine
    def post(self):
        req = tornado.escape.json_decode(self.request.body)
        url = urlparse(req.get("active", None))
        active = url.netloc + url.path
        #urlparse active
        move = req.get("move", "tab")
        if active and active != self.cgm.last_active and active != "newtab/":
            if move == "tab":
                self.cgm.coll.update_one({'url': {'$eq': active}}, {'$push': {'nav': self.cgm.last_active}},
                                         upsert=True)
            elif move == "link":
                self.cgm.coll.update_one({'url': {'$eq': active}}, {'$push': {'link': self.cgm.last_active}},
                                         upsert=True)
            print(active, move)
            self.cgm.last_active = active


def make_app():
    CGM = CGManager()
    return tornado.web.Application([
        (r"/", MainHandler, dict(cgm=CGM)),
    ])


if __name__ == "__main__":
    print("Initializing Server")
    app = make_app()
    app.listen(8888)  # TODO: change this port
    tornado.ioloop.IOLoop.current().start()