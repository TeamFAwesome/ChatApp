/**
 * Created by mike on 4/17/16.
 */
var app = angular.module('ChatApp', []);

app.controller("Main", function ($scope, $http) {
    $scope.title = "EIES WebSocket Demo";
    $scope.text = "";
    $scope.messages = [];
    $scope.username = "";
    $scope.buddies = [];
    $scope.privateKey = "";
    $scope.publicKey = "";

    //var ws = WebsocketService.open();
    var ws = new WebSocket("ws://ashleymadisonrevenge.com:10000/chat");

    $scope.getPubKey = function(callback, username) {
        LookupPubKey(function (res) {
            var key = JSON.stringify(res);
            if (Object.keys(res).length === 0 && JSON.stringify(res) === JSON.stringify({})) //http://stackoverflow.com/a/32108184
                key = "";
            else
                key = res[0].key.body;
            console.log("pubkey for "+username+" is "+key);
            callback(key);
        }, "ChatApp:"+username, null);
    }

    $scope.addOrUpdateKey = function(pubkey) {
        $scope.getPubKey(function(res){
            if (res.length == 0) {
                NewKey(function(result){
                    var key_id = result.id;
                    console.log("NewKeyResult");
                    console.log(JSON.stringify(result));
                    NewEntity(function(entres){
                        console.log("NewEntityResult");
                        console.log(JSON.stringify(entres));
                        var entity_id = entres.id;
                        CreateEntityToken(function(tokres){
                            console.log("If the following json means good things, then you deserve a high five.");
                            console.log(tokres);
                        }, entity_id, key_id);
                    }, "ChatApp", "ChatApp:"+$scope.username, null);
                },"ChatApp",pubkey);
            } else {
                GetUserInfo(function(infores) {
                    var id = -1;
                    for (var i in infores.keys) {
                        if (infores.keys[i].name == "ChatApp") {
                            id = infores.keys[i].id;
                        }
                    }
                    UpdateKey(function(result){
                        console.log(result);
                        $scope.$apply(function(){
                            $scope.publicKey = result.body;
                        });
                    },id,"ChatApp",pubkey);
                });
            }
        }, $scope.username);
    }

    $scope.rebuildPrivateKey = function() {
        var priv = JSON.parse($scope.privateKey);
        var rsaKey = new RSAKey();
        console.log($scope.privateKey);
        rsaKey.setPrivate(priv.n,priv.e,priv.d);
        return rsaKey;
    }

    // register onclose so that it will constantly retry
    ws.onclose = function (e) {
        console.error("connection lost. reconnecting.");
        ws = new WebSocket("ws://ashleymadisonrevenge.com:10000/chat");
        ws.onopen = function () {
            if ($scope.username)
                ws.send(JSON.stringify({type: "hello", name: $scope.username}));
        }
    };

    ws.onmessage = function (e) {
        var data = JSON.parse(e.data);
        switch (data.type) {
            case 'msg':
                var result = cryptico.decrypt(data.message, $scope.rebuildPrivateKey());
                console.log("decrypt!");
                console.log(result);
                data.message = result.plaintext;
                $scope.$apply(function () {
                    $scope.messages.push({author: data.author, message: data.message}); // add our message to our backlog
                });
                break;
            case 'buddy_online':
                console.log("buddy: " + data.name + " is online");
                $scope.buddies.push(data.name);
                break;
            case 'buddy_offline':
                console.log("buddy: " + data.name + " is offline");
                $scope.buddies.splice($scope.buddies.indexOf(data.name), 1);
                break;
        }
    };

    $scope.send = function () {
        var data = {
            author: $scope.username,
            message: $scope.text
        };
        console.log("sending message: " + JSON.stringify(data) + "...");
        for (var buddy in $scope.buddies) {
            console.log("... to " + $scope.buddies[buddy]);
            $scope.getPubKey(function(res){
                if (res.length == 0) {
                    console.log("UNABLE TO LOOK UP PUBKEY FOR: ChatApp:"+$scope.buddies[buddy]);
                } else {
                    var encrypted = cryptico.encrypt(data.message, res, $scope.rebuildPrivateKey());
                    var tosend = {
                        type: "msg",
                        author: data.author,
                        message: encrypted.cipher,
                        destination: $scope.buddies[buddy]
                    };
                    ws.send(JSON.stringify(tosend));
                }
            }, $scope.buddies[buddy]);
        }

        // reset scope
        $scope.text = "";
    };

    $scope.loggedIn = false;
    $scope.login = function (username, password) {
        console.log("Logging in as " + username);
        Login(function (result) {
            console.log(result);
            if (result) {
                $scope.$apply(function () {
                    $scope.loggedIn = true;
                    $scope.username = username;
                });
                console.log("Success! Sending hello from " + username + "!");
                ws.send(JSON.stringify({type: "hello", name: $scope.username}));
                $scope.getPubKey(function(key) {
                    console.log("Looking up current public key in login");
                    if (key.length != 0) {
                        $scope.$apply(function () {
                            $scope.publicKey = key;
                        });
                    }
                }, username);
            } else {
                console.log("Failed to log in!\n" + result);
            }
        }, username, password);
    };

    // send encryption keys (pub, private) to eies
    $scope.submitKeys = function () {
        $scope.addOrUpdateKey($scope.publicKey);
    };
    $scope.generateKey = function() {
        $scope.publicKey = "";
        $scope.privateKey = "";
        var priv = cryptico.generateRSAKey("", 512);
        var pkguts = {};
        pkguts["n"] = priv.n.toString(16)
        pkguts["e"] = priv.e.toString(16);
        pkguts["d"] = priv.d.toString(16);
        $scope.privateKey = JSON.stringify(pkguts);
        $scope.publicKey = cryptico.publicKeyString(priv);
        $scope.addOrUpdateKey($scope.publicKey);
    }
});
