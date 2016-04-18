var api = new WebSocket("ws://localhost:11000/api");
var pendingcalls = []

api.onclose = function (e) {
    console.error("connection lost. reconnecting.");
    function abortPending(element, index, array) {
        element["result"] = "ABORTED DUE TO DISCONNECTION";
        element["callback"](element);
    }
    pendingcalls=[]
    api = new WebSocket("ws://localhost:11000/api");
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
        returnedcall["callback"](data["result"]);
        pendingcalls.splice(array.indexOf(returnedcall), 1);
    }
    else
    {
        console.log("NOT SURE WHICH PENDING CALL ACTUALLY RETURNED A MESSAGE FROM PYTHON LAND");
        console.log(data);
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

//// BEGIN SESSION
function Login(email, password)
{
  var r;
  invoke(function(result){ r = result; }, "Login", {email: email, password: password});
  while (!r) {}
  return r;
}
function Logout()
{
  var r;
  invoke(function(result){ r = result; }, "Logout", {});
  while (!r) {}
  return r;
}
    
//// END SESSION
    
    
//// BEGIN USER INFO STUFF
function GetUserInfo()
{
  var r;
  invoke(function(result){ r = result; }, "GetUserInfo", {});
  while (!r) {}
  return r;
}
//// BEGIN USER INFO STUFF


//// BEGIN KEY STUFF
function LookupPubKey(domain, port)
{
  var r;
  invoke(function(result){ r = result; }, "LookupPubKey", {domain: domain, port: port});
  while (!r) {}
  return r;
}

function NewKey(name, body)
{
  var r;
  invoke(function(result){ r = result; }, "NewKey", {name: name, body: body});
  while (!r) {}
  return r;
}

function RetrieveKey(key_id)
{
  var r;
  invoke(function(result){ r = result; }, "RetrieveKey", {key_id: key_id});
  while (!r) {}
  return r;
}

function UpdateKey(name, body)
{
  var r;
  invoke(function(result){ r = result; }, "UpdateKey", {name: name, body: body});
  while (!r) {}
  return r;
}

function DestroyKey(key_id)
{
  var r;
  invoke(function(result){ r = result; }, "DestroyKey", {key_id});
  while (!r) {}
  return r;
}
//// END KEY STUFF


//// BEGIN ENTITY STUFF
function NewEntity(name, domain, port)
{
  var r;
  invoke(function(result){ r = result; }, "NewEntity", {name: name, domain: domain, port: port});
  while (!r) {}
  return r;
}

function RetrieveEntity(entity_id)
{
  var r;
  invoke(function(result){ r = result; }, "RetrieveEntity", {entity_id: entity_id});
  while (!r) {}
  return r;
}

function UpdateEntity(name, domain, port)
{
  var r;
  invoke(function(result){ r = result; }, "UpdateEntity", {name: name, domain: domain, port: port});
  while (!r) {}
  return r;
}

function DestroyEntity(entity_id)
{
  var r;
  invoke(function(result){ r = result; }, "DestroyEntity", {entity_id: entity_id});
  while (!r) {}
  return r;
}
//// END ENTITY STUFF


//// BEGIN ENTITY TOKEN STUFF
function CreateEntityToken(entity_id, key_id)
{
  var r;
  invoke(function(result){ r = result; }, "CreateEntityToken", {entity_id: entity_id, key_id: key_id});
  while (!r) {}
  return r;
}

function RetrieveEntityToken(token_id, session_id)
{
  var r;
  invoke(function(result){ r = result; }, "RetrieveEntity", {token_id: token_id, session_id: session_id});
  while (!r) {}
  return r;
}

function DestroyEntityToken(token_id, session_id)
{
  var r;
  invoke(function(result){ r = result; }, "DestroyEntity", {token_id: token_id, session_id: session_id});
  while (!r) {}
  return r;
}
//// END ENTITY TOKEN STUFF
