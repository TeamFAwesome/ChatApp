import tornado.ioloop
import tornado.web
import tornado.websocket
import inspect
import sys
from EIESWrapper import *
from Common import *
printerer.Instance().setPrefixer() #singleton for prefixing prints with file and number

from KeyHelper import *

clients = []

class EIESWrapperHandler(tornado.websocket.WebSocketHandler):
    def callFunctionWithJsonArguments(self, funcname, arguments):
        try:
            # check for named function on keyhelper
            if (hasattr(self.keyhelper, funcname)):
                f = getattr(self.keyhelper, funcname)
                if len(arguments)==1 and arguments["func"] != None:
                    return f()
                return f(**{key:value for key,value in arguments.items() if key in inspect.getargspec(f)[0] and not key == "func"})
            # if function wasn't on keyhelper, call it on eies OR DIE TRYING
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
        self.keyhelper = KeyHelperRuntimeHandler()
        errorcode = self.keyhelper.Init()
        if errorcode:
            sys.exit(errorcode)
        if not self.keyhelper.Load() and not self.keyhelper.Create():
            print("Failed to load or create keys", file=sys.stderr)
            sys.exit(4)
        clients.append(self)

    def on_message(self, msg):
        print("Received api call to websocket wrapper: %s" % msg)
        message = json.loads(msg)
        try:
            if not "func" in message.keys():
                message["result"] = "AMBIGUOUS FUNCTION CALLED"
                for client in clients:
                    client.write_message(json.dumps(message))
                print("UNSURE WHICH WRAPPED FUNCTION TO CALL: ",message)
            else:
                for client in clients:
                    message["result"] = client.callFunctionWithJsonArguments(message["func"], message)
                    #print("RESPONDING: %s" % json.dumps(message["result"]))
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
