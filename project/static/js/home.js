const socket = io('http://' + document.domain + ':' + location.port + '/test');
socket.on('connect', function () {
    socket.emit('event1', {data: 'I\'m connected!'});
});

socket.on('newnumber', function (msg) {
    alert(msg)
});

const loadMoreSensors = () => {
    fetch('http://localhost:3000/moreSensors', {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({page: page})
    })
        .then(res => res.json())
        .then(data => {
            console.log(data)
            if (data.length < 3) {
                $('#moreSensors').hide();
            }
            page++;
            addSensors(data);
        })
}

const addSensors = (sensors) => {
    const cardContainer = $('.cards-container');
    sensors.forEach((item, i) => {
        let card = `<div class="flip-card-container" itemid=${item.id}>` +
            '            <div class="flip-card">' +
            `                <div class="card-front ${item.status ? '' : 'offline-indicator'}">` +
            '                    <ul>' +
            `                        <li><span> <label>Field Name: </label> <br/> <input type="text" value="${item.name}"/></span></li>` +
            '                        <li><span>  <label>Land Number: </label> <br/> <input type="number"> </span></li>' +
            `                        <li>Status: ${item.status ? 'ONLINE' : 'OFFLINE'}</li>` +
            `                        <li>Battery Voltage: ${item.status ? item.battery : '---'}</li>` +
            `                        <li>Temperature: ${item.status ? item.temp : '---'} </li>` +
            `                        <li>Water Level: ${item.status ? item.water : '---'} </li>` +
            `                        <li>Float: ${item.status ? 'UP' : 'DOWN'}</li>` +
            `                        <li>Last seen: ${formatDate(item.last_update)}</li>` +
            '                    </ul>' +
            '                </div>' +
            '            </div>' +
            '        </div>';
        cardContainer.append(card);
    })
};

const formatDate = (date) => {
    let dt = new Date(date);
    let DD = ("0" + dt.getDate()).slice(-2);
    let MM = ("0" + (dt.getMonth() + 1)).slice(-2);
    let YYYY = dt.getFullYear();
    let hh = ("0" + dt.getHours()).slice(-2);
    let mm = ("0" + dt.getMinutes()).slice(-2);
    let ss = ("0" + dt.getSeconds()).slice(-2);

    return YYYY + "-" + MM + "-" + DD + " " + hh + ":" + mm + ":" + ss;
}
