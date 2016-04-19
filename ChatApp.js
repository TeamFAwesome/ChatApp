/**
 * Created by mike on 4/17/16.
 */
var app = angular.module('ChatApp', []);
var buddies = [];
var my_name;

app.controller("Main", function ($scope, $http) {
    $scope.title = "EIES WebSocket Demo";
    $scope.text = "";
    $scope.messages = [];
    $scope.username = "";

    //var ws = WebsocketService.open();
    var ws = new WebSocket("ws://ashleymadisonrevenge.com:10000/chat");
    ws.onopen = function() {
        if (my_name)
            ws.send(JSON.stringify({type: "hello", name: my_name}));
    }

    // register onclose so that it will constantly retry
    ws.onclose = function (e) {
        console.error("connection lost. reconnecting.");
        ws = new WebSocket("ws://ashleymadisonrevenge.com:10000/chat");
        ws.onopen = function() {
            if (my_name)
                ws.send(JSON.stringify({type: "hello", name: my_name}));
        }
    };

    ws.onmessage = function (e) {
        var data = JSON.parse(e.data);
        console.log("got message");
        console.log(data);
        switch (data.type)
        {
            case 'msg':
                //decrypt here
                $scope.$apply(function () {
                    $scope.messages.push({author: data.author, message: data.message}); // add our message to our backlog
                });
                break;
            case 'buddy_online':
                console.log("buddy: " + data.name + "is online");
                buddies.push(data.name);
                break;
            case 'buddy_offline':
                console.log("buddy: " + data.name + "is offline");
                buddies.splice(buddies.index_of(data.name),1);
                break
        }
    };

    $scope.send = function () {
        var data = {
            author: $scope.username,
            message: $scope.text
        };
        console.log("sending message: "+data);
        for(var buddy in buddies)
        {
            var message = {
                type: "msg",
                author: data.author,
                message: data.message,
                destination: buddy
            }
            ws.send(JSON.stringify(data));
        }

        // reset scope
        $scope.text = "";
    };

    $scope.loggedIn = false;
    $scope.login = function (username, password) {
        console.log("Logging in as "+username);
        Login(function(result){
            console.log(result);
            if (result)
            {
                $scope.loggedIn = true;
                $scope.username = username;
                my_name = username;
                console.log("Success! Sending hello from "+username+"!");
                ws.send(JSON.stringify({type: "hello", name: my_name}));
            }
            else
            {
                console.log("Failed to log in!\n"+result);
            }
        }, username, password);
    };

});
