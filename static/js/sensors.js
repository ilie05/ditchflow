const socket = io(`http://${document.domain}:${location.port}/notification`);
socket.on('connect', function () {
    console.log("Connected")
});

socket.on('sensor_notification', function (data) {
    console.log(data);
    let card = $(`.cards-container [itemid=${data.id}]`);
    if (!card.length) return;

    $(card).find('li.sName').text(`Sensor Name: ${data.name}`);
    $(card).find('li.sStatus').text(`Status: ONLINE`);
    $(card).find('li.sBattery').text(`Battery Voltage: ${data.battery} V`);
    $(card).find('li.sTemperature').text(`Temperature: ${data.temperature} °F`);
    $(card).find('li.sFloat').text(`Float: ${data.float ? 'UP' : 'DOWN'}`);
    $(card).find('li.sLastSeen').text(`Last seen: ${data.last_update}`);
    $(card).find('li.sSignal').text(`Signal Strength: ${data.signal_strength}`);

    $(card).find('.card-front').removeClass('offline-indicator');
});

socket.on('goOfflineSensor', function (id) {
    console.log(`The sensor with id ${id} went offline.`)
    let card = $(`.cards-container [itemid=${id}]`);
    if (!card.length) return;

    $(card).find('li.sStatus').text('Status: OFFLINE');
    $(card).find('li.sSignal').text('Signal Strength: ---');
    $(card).find('li.sBattery').text('Battery Voltage: ---');
    $(card).find('li.sTemperature').text('Temperature: ---');
    $(card).find('li.sFloat').text('Float: ---');

    $(card).find('.card-front').addClass('offline-indicator');
});

const MAIN_URL = `http://${document.domain}:${location.port}`;

const deleteSensor = (context) => {
    const card = $(context).closest(".flip-card-container");
    const sensorId = card.attr('itemid');
    fetch(`${MAIN_URL}/sensors`, {
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
            }
        });
}

const updateLandNumber = (context) => {
    const card = $(context).closest(".flip-card-container");
    const sensorId = card.attr('itemid');
    const landNumber = $(context).val();
    if (!landNumber) return

    fetch(`${MAIN_URL}/sensors`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({sensorId, landNumber})
    })
        .then(res => {
            if (res.ok) {
                $(card).find('.card-info').show();
                setInterval(() => $(card).find('.card-info').hide(),3000);
            }
        });
}

const updateNotes = (context) => {
    const card = $(context).closest(".flip-card-container");
    const sensorId = card.attr('itemid');
    const notes = $(context).val();
    if (!notes) return

    fetch(`${MAIN_URL}/sensors/notes`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({sensorId, notes})
    })
        .then(res => {
            if (res.ok) {
                $(card).find('.card-info.notes').show();
                setInterval(() => $(card).find('.card-info.notes').hide(),3000);
            }
        });
}
