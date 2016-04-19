/*
 *  Eric McCann 2016
 */
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
    //console.log("got message");
    //console.log(e.data);
    if (e.data == "web socket explosion")
    {
      console.log("fatal exception occured in python-land. purging pending call queue to unblock invokes")
      for (var pendingcall in pendingcalls)
      {
        pendingcall["callback"](e.data);
      }
      pendingcalls = []
      return;
    }
    var data = JSON.parse(e.data);
    returnedcall = null;
    for (var pendingcall in pendingcalls)
    {
        if (data.func == pendingcalls[pendingcall].args.func)
        {
            //console.log("Found pending call with correct func");
            pendingargs = pendingcalls[pendingcall].args;
        
            returnedcall = pendingcalls[pendingcall];
            for (var arg in pendingargs)
            {
                if (pendingargs[arg] != data[arg])
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
        /*console.log("received response!");
        console.log("returned:");
        console.log(returnedcall);
        console.log("data:");
        console.log(data);*/
        returnedcall.callback(data.result);
        pendingcalls.splice(pendingcalls.indexOf(returnedcall), 1);
    }
    else
    {
        console.log("NOT SURE WHICH PENDING CALL ACTUALLY RETURNED A MESSAGE FROM PYTHON LAND");
        console.log(data);
    }
};

var invoke = function (callback, funcname, args) {
    if (! (callback instanceof Function))
    {
        console.log("ERROR: no callback function specified!");
        return;
    }
    pendingcall = {};
    pendingcall["callback"] = callback;
    pendingcall["func"] = funcname;
    pendingcall["args"] = args;
    pendingcall["args"].func = funcname;
    pendingcalls.push(pendingcall);
    api.send(JSON.stringify(pendingcall["args"]));
}

//// BEGIN SESSION
function Login(callback, email, password)
{
  invoke(callback, "Login", {email: email, password: password});
}
function Logout(callback)
{
  invoke(callback, "Logout", {});
}
    
//// END SESSION
    
    
//// BEGIN USER INFO STUFF
function GetUserInfo(callback, user_id=null)
{
  invoke(callback, "GetUserInfo", {user_id: user_id});
}
//// BEGIN USER INFO STUFF


//// BEGIN KEY STUFF
function LookupPubKey(callback, domain, port)
{
  invoke(callback, "LookupPubKey", {domain: domain, port: port});
}

function NewKey(callback, name, body)
{
  invoke(callback, "NewKey", {name: name, body: body});
}

function RetrieveKey(callback, key_id)
{
  invoke(callback, "RetrieveKey", {key_id: key_id});
}

function UpdateKey(callback, name, body)
{
  invoke(callback, "UpdateKey", {name: name, body: body});
}

function DestroyKey(callback, key_id)
{
  invoke(callback, "DestroyKey", {key_id});
}
//// END KEY STUFF


//// BEGIN ENTITY STUFF
function NewEntity(callback, name, domain, port)
{
  invoke(callback, "NewEntity", {name: name, domain: domain, port: port});
}

function RetrieveEntity(callback, entity_id)
{
  invoke(callback, "RetrieveEntity", {entity_id: entity_id});
}

function UpdateEntity(callback, name, domain, port)
{
  invoke(callback, "UpdateEntity", {name: name, domain: domain, port: port});
}

function DestroyEntity(callback, entity_id)
{
  invoke(callback, "DestroyEntity", {entity_id: entity_id});
}
//// END ENTITY STUFF


//// BEGIN ENTITY TOKEN STUFF
function CreateEntityToken(callback, entity_id, key_id)
{
  invoke(callback, "CreateEntityToken", {entity_id: entity_id, key_id: key_id});
}

function RetrieveEntityToken(callback, token_id, session_id)
{
  invoke(callback, "RetrieveEntityToken", {token_id: token_id, session_id: session_id});
}

function DestroyEntityToken(callback, token_id, session_id)
{
  invoke(callback, "DestroyEntityToken", {token_id: token_id, session_id: session_id});
}
//// END ENTITY TOKEN STUFF
