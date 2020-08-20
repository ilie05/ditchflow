const socket = io('http://' + document.domain + ':' + location.port + '/test');
socket.on('connect', function () {
    socket.emit('event1', {data: 'I\'m connected!'});
});

socket.on('newnumber', function(msg) {
    alert(msg)
})