import tornado.ioloop
import tornado.web
import tornado.websocket
from EIESWrapper import *
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
    def callFunctionWithJsonArguments(self, funcname, arguments):
        f = getattr(self.eies, funcname)
        return f(**{key:value for key,value in arguments.items() if key in inspect.getargspec(f)[0] and not key == "func"})

    def check_origin(self, origin):
        return True

    def open(self, *args):
        print("open", "EIESWrapperHelper")
        self.eies = EIESWrapper()
        clients.append(self)

    def on_message(self, msg):
        print("Received api call to websocket wrapper: %s" % msg)
        message = json.loads(msg)
        print(message)
        try:
            if not "func" in message.keys():
                message["result"] = "AMBIGUOUS FUNCTION CALLED"
                for client in clients:
                    client.write_message(json.dumps(message))
                print("UNSURE WHICH WRAPPED FUNCTION TO CALL: ",message)
            else:
                for client in clients:
                    message["result"] = client.callFunctionWithJsonArguments(message["func"], message)
                    client.write_message(json.dumps(message))
        except:
            message["result"] = "general websocket explosion"
            print("Fatal exception ocurred while trying to handle arguments and invoke. ungh.")
            for client in clients:
                client.write_message(json.dumps(message))
            raise

    def on_close(self):
        clients.remove(self)


# app = tornado.web.Application([(r'/chat', WebSocketChatHandler), (r'/', IndexHandler)])
app = tornado.web.Application([(r'/chat', WebSocketChatHandler)])
api = tornado.web.Application([(r'/api', EIESWrapperHandler)])

app.listen(10000)
api.listen(11000)
tornado.ioloop.IOLoop.instance().start()
