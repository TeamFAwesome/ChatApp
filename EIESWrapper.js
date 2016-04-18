var api = new WebSocket("ws://localhost:11000/api");
var pendingcalls = []

api.onclose = function (e) {
    console.error("connection lost. reconnecting.");
    function abortPending(element, index, array) {
        element["result"] = "ABORTED DUE TO DISCONNECTION";
        element["callback"](element);
    }
    pendingcalls=[]
    api = new WebSocket("ws://localhost:10000/chat");
};

api.onmessage = function (e) {
    var data = JSON.parse(e.data);
    console.log("got message");
    console.log(data);
    returnedcall = null;
    for (var pendingcall in pendingcalls)
    {
        if (data.func == pendingcall["func"])
        {
            pendingargs = json.parse(pendingcall["args"]);
            returnedargs = json.parse(data);
            returnedcall = pendingcall;
            for (var arg in pendingargs)
            {
                if (pendingargs[arg] != returnedargs[arg])
                {
                    returnedcall = null;
                    break;
                }
            }
            if (returnedcall != null)
                break;
        }
    }
    if (returnedcall != null)
    {
        $scope.$apply(function () {
            pendingcall["callback"](returnedcall["result"]);
        })
        pendingcalls.splice(array.indexOf(returnedcall), 1)
    }
    else
    {
        console.log("NOT SURE WHICH PENDING CALL ACTUALLY RETURNED A MESSAGE FROM PYTHON LAND");
    }
};

var invoke = function (callback, funcname, args) {
    pendingcall = {};
    pendingcall["callback"] = callback;
    pendingcall["func"] = funcname;
    pendingcall["args"] = json.stringify(args);
    pendingcall["args"]["func"] = funcname;
    pendingcalls.Add(pendingcall)
    ws.send(JSON.stringify(pendingcall["args"]));
}


