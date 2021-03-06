const socket = io(`http://${document.domain}:${location.port}/notification`);
socket.on('connect', function () {
    console.log("Connected")
});

socket.on('valve_notification', function (data) {
    console.log(data);
    let card = $(`.cards-container [itemid=${data.id}]`);
    if (!card.length) return;

    $(card).find('li.vName').text(`Valve Name: ${data.name}`);
    $(card).find('li.vStatus').text(`Status: ONLINE`);
    $(card).find('li.vActuatorStatus').text(`Actuator Status: ${data.actuator_status}`);
    $(card).find('li.vActuatorSetPosition button').show();
    $(card).find('li.vBattery').text(`Battery Voltage: ${data.battery} V`);
    $(card).find('li.vTemperature').text(`Temperature: ${data.temperature} °F`);
    $(card).find('li.vLastSeen').text(`Last seen: ${data.last_update}`);

    if (data.actuator_status === 'Moving') {
        $(card).find('li.vActuatorActualPosition').text(`Actuator Actual Position: ---`);
    } else {
        $(card).find('li.vActuatorActualPosition').text(`Actuator Actual Position: ${data.actuator_position}%`);
    }

    if (data.water === null) {
        $(card).find('li.vWater').text(`Water Level: ---`);
    } else {
        $(card).find('li.vWater').text(`Water Level: ${data.water} inches`);
    }

    $(card).find('.card-front').removeClass('offline-indicator');
});

socket.on('goOfflineValve', function (id) {
    console.log(`The valve with id ${id} went offline.`)
    let card = $(`.cards-container [itemid=${id}]`);
    if (!card.length) return;

    $(card).find('li.vStatus').text('Status: OFFLINE');
    $(card).find('li.vActuatorStatus').text('Actuator Status: ---');
    $(card).find('li.vActuatorActualPosition').text('Actuator Actual Position: ---');
    $(card).find('li.vActuatorActualPosition').text('Actuator Actual Position: ---');
    $(card).find('li.vActuatorSetPosition button').hide();
    $(card).find('li.vWater').text('Water Level: ---');
    $(card).find('li.vBattery').text('Battery Voltage: ---');
    $(card).find('li.vTemperature').text('Temperature: ---');

    $(card).find('.card-front').addClass('offline-indicator');
});

const MAIN_URL = `http://${document.domain}:${location.port}`;

const deleteValve = (context) => {
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
                $(card).find('.card-info').show();
                setInterval(() => $(card).find('.card-info').hide(), 3000);
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

let INTERVAL;
const calibrateValves = () => {
    const message = $('.calibrate .calib-message');

    message.text('Calibration started!');
    message.show();
    fetch(`${MAIN_URL}/calibrate`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
        },
    }).then(res => {
        if (res.ok) message.text('Calibration finished successful!');
        else message.text('Calibration failed!');

        clearInterval(INTERVAL);
        INTERVAL = setInterval(() => message.hide(), 3000);
    }).catch(err => {
        message.text('Calibration failed!');
        clearInterval(INTERVAL);
        INTERVAL = setInterval(() => message.hide(), 3000);
    })
}