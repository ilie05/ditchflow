const socket = io(`http://${document.domain}:${location.port}/sensor`);
socket.on('connect', function () {
    console.log("Connected")
});

socket.on('newnumber', function (msg) {
    console.log(msg)
});
