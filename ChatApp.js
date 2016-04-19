/**
 * Created by mike on 4/17/16.
 */
var app = angular.module('ChatApp', []);

app.controller("Main", function ($scope, $http) {
    $scope.title = "EIES WebSocket Demo";
    $scope.text = "";
    $scope.messages = [];
    $scope.username = "";

    //var ws = WebsocketService.open();
    var ws = new WebSocket("ws://localhost:10000/chat");

    // register onclose so that it will constantly retry
    ws.onclose = function (e) {
        console.error("connection lost. reconnecting.");
        ws = new WebSocket("ws://localhost:10000/chat");
    };

    ws.onmessage = function (e) {
        var data = JSON.parse(e.data);
        console.log("got message");
        console.log(data);
        $scope.$apply(function () {
            $scope.messages.push(data); // add our message to our backlog
        })
    };

    $scope.send = function () {
        // format message
        var data = {
            author: $scope.username,
            message: $scope.text
        };
        console.log("sending message");
        console.log(data);

        //ENCRYPT AND GET SHIT DONE HERE

        // this sends message to websocket
        ws.send(JSON.stringify(data));

        // reset scope
        $scope.text = "";
    };

    $scope.loggedIn = false;
    $scope.login = function (username, password) {
        console.log(username + "," + password);
        $scope.loggedIn = true; // when this variable changes the view changes automatically. ohhh. magic.

        // THIS IS WHERE YOU CAN ADD SHIT FOR AFTER LOGIN.
        //$scope.username gets tracked and is used for messages now.

    };

});
