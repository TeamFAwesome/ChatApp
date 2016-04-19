/**
 * Created by mike on 4/17/16.
 */
var app = angular.module('ChatApp', []);

app.controller("Main", function ($scope, $http) {
    $scope.title = "EIES WebSocket Demo";
    $scope.author = "";
    $scope.text = "";
    $scope.messages = [];

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
        //WebsocketService.sendMessage($scope.author, $scope.text);
        var data = {
            author: $scope.author,
            message: $scope.text
        };
        console.log("sending message");
        console.log(data);
        ws.send(JSON.stringify(data));

        // reset scope
        $scope.text = "";
    };

});
