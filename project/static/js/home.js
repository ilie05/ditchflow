const loadMoreSensors = (hide = true, noItems) => {
    fetch('http://localhost:3000/moreSensors', {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({page, noItems})
    })
        .then(res => res.json())
        .then(data => {
            if (data.length < 3 && hide) {
                $('#moreSensors').hide();
            }
            if (hide) page++;
            addSensors(data);
        })
}

const addSensors = (sensors) => {
    const cardContainer = $('.cards-container');
    sensors.forEach((item, i) => {
        let card = `<div class="flip-card-container" itemid=${item.id}>` +
            '            <div class="flip-card">' +
            `                <div class="card-front ${item.status ? '' : 'offline-indicator'}">` +
            '                    <img class="delete-card" src="../static/images/delete.jpeg" onclick="deleteSensor(this)" />' +
            '                    <ul>' +
            `                        <li><span> <label>Field Name: </label> <br/> <input type="text" value="${item.name}"/></span></li>` +
            '                        <li><span>  <label>Land Number: </label> <br/> <input type="number"> </span></li>' +
            `                        <li>Status: ${item.status ? 'ONLINE' : 'OFFLINE'}</li>` +
            `                        <li>Battery Voltage: ${item.status ? item.battery + ' V' : '---'}</li>` +
            `                        <li>Temperature: ${item.status ? item.temp + ' F' : '---'} </li>` +
            `                        <li>Water Level: ${item.status ? item.water + ' inches' : '---'} </li>` +
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

const deleteSensor = (context) => {
    const card = $(context).closest(".flip-card-container");
    const sensorId = card.attr('itemid');
    console.log(sensorId);
    fetch('http://localhost:3000', {
        method: 'DELETE',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({sensorId})
    })
        .then(res => {
            if (res.ok) {
                card.remove();
                loadMoreSensors(false, 1);
            }
        });
}


// {\n} on message page
// battery min 11 V
// 30 min check database for online status