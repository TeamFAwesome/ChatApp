import tornado.ioloop
import tornado.web
import tornado.websocket
from EIESWrapper import *
import inspect

clients = []

class EIESWrapperHandler(tornado.websocket.WebSocketHandler):
    def callFunctionWithJsonArguments(self, funcname, arguments):
        try:
            f = getattr(self.eies, funcname)
            return f(**{key:value for key,value in arguments.items() if key in inspect.getargspec(f)[0] and not key == "func"})
        except TypeError as e:
            return {"error": str(e)}
        except:
            raise

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

api = tornado.web.Application([(r'/api', EIESWrapperHandler)])
api.listen(11000)
tornado.ioloop.IOLoop.instance().start()
