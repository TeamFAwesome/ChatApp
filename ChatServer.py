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
        self.set_nodelay(True)
        print("open", "WebSocketChatHandler")
        namelessclients.append(self)
        print("#nameless = %d" % len(namelessclients))
        self.name = None

    def on_message(self, message):
        print("RECEIVED: "+message);
        data = json.loads(message)
        if data["type"] == "hello":
            self.name = data["name"]
            if self in namelessclients:
                namelessclients.remove(self)
            clients[self.name] = self
            self.send_buddy_online()
            print("HELLO %s! %d nameless, %d named" % (self.name, len(namelessclients), len(clients)))
        elif data["type"] == "msg":
            if not data["destination"] in clients.keys():
                print("Error: unknown message destination\n\t%s" % data)
            else:
                clients[data["destination"]].write_message(message)
        else:
            print("Warning: received unknown message from client: %s" % data)

    def send_buddy_online(self):
        print("Sending online status of %s" % self.name)
        for c in clients:
            try:
                clients[c].write_message(json.dumps({"type": "buddy_online", "name": self.name}))
            except tornado.websocket.WebSocketClosedError:
                pass
            try:
                self.write_message(json.dumps({"type": "buddy_online", "name": c}))
            except tornado.websocket.WebSocketClosedError:
                pass

    def send_buddy_offline(self):
        print("Sending offline status of %s" % self.name)
        for c in clients:
            try:
                clients[c].write_message(json.dumps({"type": "buddy_offline", "name": self.name}))
            except tornado.websocket.WebSocketClosedError:
                pass

    def on_close(self):
        if self in namelessclients:
            namelessclients.remove(self)
        else:
            if self in clients:
                del clients[self.name]
            self.send_buddy_offline()

    def __str__(self):
        if self.name and self.name != None:
            return self.name
        return "[UNKNOWN]"


app = tornado.web.Application([(r'/chat', WebSocketChatHandler)])
app.listen(10000)
tornado.ioloop.IOLoop.instance().start()
