import tornado.ioloop
import tornado.web
import tornado.websocket
import EIESWrapper
import inspect

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

class EIESWrapperHandler(tornado.websocket.WebSocketHandler):
    def callFunctionWithJsonArguments(self, eies, funcname, arguments):
        f = getattr(eies, funcname)
        return f(**{key:value for key,value in arguments.items() if key in inspect.getargspec(f)[0] and not key == "func"})

    def __init__(self):
        super(EIESWrapperHandler, self).__init__()
        if attr(EIESWrapperHandler, "eises") == None:
            EIESWrapperHandler.eises = {}

    def check_origin(self, origin):
        return True

    def open(self, *args):
        print("open", "EIESWrapperHelper")
        clients.append(self)
        self.eises[self] = EIESWrapper()

    def on_message(self, message):
        if not "func" in message.keys():
            print("UNSURE WHICH WRAPPED FUNCTION TO CALL: ",message)
        else:
            for client in clients:
                message["result"] = self.callFunctionWithJsonArguemtns(self.eises[client], message["func"], message)
                client.write_message(message)

    def on_close(self):
        clients.remove(self)
        self.eises


# app = tornado.web.Application([(r'/chat', WebSocketChatHandler), (r'/', IndexHandler)])
app = tornado.web.Application([(r'/chat', WebSocketChatHandler)])
api = tornado.web.Application([(r'/api', EIESWrapperHandler)])

app.listen(10000)
api.listen(11000)
tornado.ioloop.IOLoop.instance().start()
