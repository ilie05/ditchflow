const socket = io(`http://${document.domain}:${location.port}/notification`);
socket.on('connect', function () {
    console.log("Connected")
});

socket.on('valve_notification', function (data) {
    console.log(data);
    let card = $(`.cards-container [itemid=${data.id}]`);
    if (!card.length) return;

    $(card).find('li.vName').text(`Valve Name: ${data.name}`);

    $(card).find('li.vActuatorStatus').text(`Actuator Status: ${data.actuator_status}`);
    $(card).find('li.vWater').text(`Water Level: ${data.water} inches`);
    $(card).find('li.vBattery').text(`Battery Voltage: ${data.battery} V`);
    $(card).find('li.vTemperature').text(`Temperature: ${data.temperature} °F`);
    $(card).find('li.vLastSeen').text(`Last seen: ${data.last_update}`);

    if (data.actuator_status === 'Moving'){
        $(card).find('li.vActuatorActualPosition').text(`Actuator Actual Position: ---`);
    }else {
        $(card).find('li.vActuatorActualPosition').text(`Actuator Actual Position: ${data.actuator_position}%`);
    }

    $(card).find('.card-front').removeClass('offline-indicator');
});

socket.on('goOfflineValve', function (id) {
    console.log(`The sensor with id ${id} went offline.`)
    let card = $(`.cards-container [itemid=${id}]`);
    if (!card.length) return;

    $(card).find('li.sStatus').text('Status: OFFLINE');
    $(card).find('li.sWater').text('Water Level: ---');
    $(card).find('li.sBattery').text('Battery Voltage: ---');
    $(card).find('li.sTemperature').text('Temperature: ---');
    $(card).find('li.sFloat').text('Float: ---');

    $(card).find('.card-front').addClass('offline-indicator');
});

const MAIN_URL = `http://${document.domain}:${location.port}`;

const deleteSensor = (context) => {
    const card = $(context).closest(".flip-card-container");
    const valveId = card.attr('itemid');
    fetch(`${MAIN_URL}/valves`, {
        method: 'DELETE',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({valveId})
    })
        .then(res => {
            if (res.ok) {
                card.remove();
            }
        });
}

const updateLandNumber = (context) => {
    const card = $(context).closest(".flip-card-container");
    const valveId = card.attr('itemid');
    const landNumber = $(context).val();
    if (!landNumber) return

    fetch(`${MAIN_URL}/valves`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({valveId, landNumber})
    })
        .then(res => {
            if (res.ok) {
                $(card).find('.card-error').hide();
            } else {
                if (res.status === 409) {
                    // land number already exists
                    $(card).find('.card-error').show();
                }
            }
        });
}

const sendPosition = (context) => {
    const card = $(context).closest(".flip-card-container");
    const valveId = card.attr('itemid');
    const position = card.find('.vActuatorSetPosition input').val();
    if (position === '' || position === undefined || position === null || Number(position) < 0 || Number(position) > 100) {
        return;
    }
    console.log((position));
}
