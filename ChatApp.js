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
            callback(key);
        }, "ChatApp:"+username, null);
    }

    $scope.addOrUpdateKey = function(pubkey) {
        $scope.getPubKey(function(res){
            if (res.length == 0) {
                NewKey(function(result){
                    var key_id = result.id;
                    NewEntity(function(entres){
                        var entity_id = entres.id;
                        CreateEntityToken(function(tokres){
                            console.log("EIES has been initialized to allow you to decrypt messages sent by other ChatApp users");
                        }, entity_id, key_id);
                    }, "ChatApp", "ChatApp:"+$scope.username, null);
                },"ChatApp",pubkey);
            } else {
                GetUserInfo(function(infores) {
                    var id = -1;
                    for (var i in infores.keys) {
                        if (infores.keys[i].name == "ChatApp") {
                            id = infores.keys[i].id;
                            break;
                        }
                    }
                    if (id != -1)
                        UpdateKey(function(result){
                            if (!result["id"])
                                console.error(result);
                            else
                                console.log("Updating your public key stored in EIES");
                        },id,"ChatApp",pubkey);
                });
            }
        }, $scope.username);
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
                Decrypt(function(dec) {
                    if (!dec || dec["error"])
                        console.error("Failed to decrypt message from "+data.author+" (to: "+data.destination+")");
                    else
                        $scope.$apply(function () {
                            $scope.messages.push({author: data.author, message: dec.decrypted}); // add our message to our backlog
                        });
                }, data.message);
                break;
            case 'buddy_online':
                if (data.name != $scope.username) {
                    $scope.$apply(function () {
                        //show buddy statusd notification
                        $scope.messages.push({author: data.name, message: "has come online!", buddystate: 'online'});
                    });
                    console.log("buddy: " + data.name + " is online");
                    $scope.buddies.push(data.name);
                }
                break;
            case 'buddy_offline':
                if (data.name != $scope.username) {
                    $scope.$apply(function () {
                        //show buddy statusd notification
                        $scope.messages.push({author: data.name, message: "has gone offline!", buddystate: 'offline'});
                    });
                    console.log("buddy: " + data.name + " is offline");
                    $scope.buddies.splice($scope.buddies.indexOf(data.name), 1);
                }
                break;
        }
    };

    $scope.send = function () {
        var data = {
            author: $scope.username,
            message: $scope.text
        };
        $scope.messages.push(data);
        for (var b in $scope.buddies) {
            var buddy = $scope.buddies[b];
            $scope.getPubKey(function(res){
                if (res.length == 0) {
                    console.log("UNABLE TO LOOK UP PUBKEY FOR: ChatApp:"+buddy);
                } else {
                    Encrypt(function(enc) {
                        var tosend = {
                            type: "msg",
                            author: data.author,
                            message: enc.encrypted,
                            destination: buddy
                        };
                        console.log(tosend)
                        ws.send(JSON.stringify(tosend));
                    }, data.message, res);
                }
            }, buddy);
        }

        // reset scope
        $scope.text = "";
    };

    $scope.loggedIn = false;
    $scope.login = function (username, password) {
        console.log("Logging in as " + username);
        Login(function (result) {
            if (result) {
                $scope.$apply(function () {
                    $scope.loggedIn = true;
                    $scope.username = username;
                });
                console.log("Success! Sending hello from " + username + "!");
                ws.send(JSON.stringify({type: "hello", name: $scope.username}));
                $scope.getPubKey(function(key) {
                    if (key.length != 0) {
                        $scope.$apply(function () {
                            $scope.publicKey = key;
                        });
                    }
                    GetPrivateKey(function(r) {
                        if (r && !r["error"]) {
                            var priv = r.key;
                            $scope.$apply(function() {
                                $scope.privateKey = priv.text;
                            });
                        }
                        GetPublicKey(function(s) {
                            if (s && !s["error"]) {
                                var pub = s.key;
                                $scope.$apply(function() {
                                    $scope.publicKey = pub.text;
                                });
                                $scope.addOrUpdateKey($scope.publicKey);
                            }
                        });
                    });
                }, username);
            } else {
                console.log("Failed to log in!\n" + result);
            }
        }, username, password);
    };

    // send encryption keys (pub, private) to eies
    $scope.submitKeys = function () {
        InterpretAndWritePublic(function(result) {
            if (result && !result["error"]) {
                $scope.$apply(function() {
                    var pub = s.key;
                    $scope.$apply(function() {
                        $scope.publicKey = pub.text;
                    });
                    $scope.addOrUpdateKey($scope.publicKey);
                });
            }
        }, $scope.publicKey);
        InterpretAndWritePrivate(function(result) {
            if (result && !result["error"]) {
                $scope.$apply(function() {
                    var priv = result.key;
                    $scope.$apply(function() {
                        $scope.privateKey = priv.text;
                    });
                });
            }
        }, $scope.privateKey);
    };
    $scope.generateKey = function() {
        RegenerateKeyPair(function(result) {
            if (result && !result["error"]) {
                var priv = result.private;
                var pub = result.public;
                $scope.$apply(function() {
                    $scope.privateKey = priv.text;
                    $scope.publicKey = pub.text;
                });
                $scope.addOrUpdateKey($scope.publicKey);
            }
        });
    }
});
