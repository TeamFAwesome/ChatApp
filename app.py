import tornado.ioloop
import tornado.web
import tornado.websocket

clients = []

# hack in EIES entity here.
# be sure to serve over 0.0.0.0:10000 so that ChatApp can find the endpoint

class WebSocketChatHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self, *args):
        print("open", "WebSocketChatHandler")
        clients.append(self)

    def on_message(self, message):
        print(message)
        for client in clients:
            client.write_message(message)

    def on_close(self):
        clients.remove(self)


# app = tornado.web.Application([(r'/chat', WebSocketChatHandler), (r'/', IndexHandler)])
app = tornado.web.Application([(r'/chat', WebSocketChatHandler)])

app.listen(10000)
tornado.ioloop.IOLoop.instance().start()
