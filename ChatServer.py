import tornado.ioloop
import tornado.web
import tornado.websocket
import inspect
import json

clients = {}
namelessclients=[]

class WebSocketChatHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self, *args):
        print("open", "WebSocketChatHandler")
        namelessclients.append(self)
        print("#nameless = %d" % len(namelessclients))
        self.name = None

    def on_message(self, message):
        data = json.loads(message)
        if data["type"] == "hello":
            self.name = data["name"]
            if self in namelessclients:
                namelessclients.remove(self)
            if not self.name in clients:
                clients[self.name] = self
                self.send_buddy_online()
            print("HELLO %s ! %d nameless" % (self.name, len(namelessclients)))
        elif data["type"] == "msg":
            if not data["destination"] in clients.keys():
                print("Error: unknown message destination\n\t%s" % data)
            else:
                clients[data["destination"]].write_message(message)
        else:
            print("Warning: received unknown message from client: %s" % data)

    def send_buddy_online(self):
        for c in clients:
            clients[c].write_message(json.dumps({"msg": "buddy_online", "name": self.name}))

    def send_buddy_offline(self):
        for c in clients:
            clients[c].write_message(json.dumps({"msg": "buddy_offline", "name": self.name}))

    def on_close(self):
        if self in namelessclients:
            namelessclients.remove(self)
        else:
            del clients[self.name]
            self.send_buddy_offline()

    def __str__(self):
        if self.name and self.name != None:
            return self.name
        return "[UNKNOWN]"


app = tornado.web.Application([(r'/chat', WebSocketChatHandler)])
app.listen(10000)
tornado.ioloop.IOLoop.instance().start()
