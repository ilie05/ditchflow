const socket = io(`http://${document.domain}:${location.port}/notification`);
socket.on('connect', function () {
    console.log("Connected")
});

socket.on('check_notification', function (data) {
    console.log(data);
    let card = $(`.cards-container [itemid=${data.id}]`);
    if (!card.length) return;

    $(card).find('li.cName').text(`Check Name: ${data.name}`);
    $(card).find('li.cStatus').text(`Status: ONLINE`);
    $(card).find('li.cActuatorStatus').text(`Actuator Status: ${data.actuator_status}`);
    $(card).find('li.cActuatorSetPosition button').show();
    $(card).find('li.cBattery').text(`Battery Voltage: ${data.battery} V`);
    $(card).find('li.cTemperature').text(`Temperature: ${data.temperature} °F`);
    $(card).find('li.cLastSeen').text(`Last seen: ${data.last_update}`);

    if (data.actuator_status === 'Moving') {
        $(card).find('li.cActuatorActualPosition').text(`Actuator Actual Position: ---`);
    } else {
        $(card).find('li.cActuatorActualPosition').text(`Actuator Actual Position: ${data.actuator_position}%`);
    }

    if (data.water === null) {
        $(card).find('li.cWater').text(`Water Level: ---`);
    } else {
        $(card).find('li.cWater').text(`Water Level: ${data.water} inches`);
    }

    $(card).find('.card-front').removeClass('offline-indicator');
});

socket.on('goOfflineCheck', function (id) {
    console.log(`The check with id ${id} went offline.`)
    let card = $(`.cards-container [itemid=${id}]`);
    if (!card.length) return;

    $(card).find('li.cStatus').text('Status: OFFLINE');
    $(card).find('li.cActuatorStatus').text('Actuator Status: ---');
    $(card).find('li.cActuatorActualPosition').text('Actuator Actual Position: ---');
    $(card).find('li.cActuatorActualPosition').text('Actuator Actual Position: ---');
    $(card).find('li.cActuatorSetPosition button').hide();
    $(card).find('li.cWater').text('Water Level: ---');
    $(card).find('li.cBattery').text('Battery Voltage: ---');
    $(card).find('li.cTemperature').text('Temperature: ---');

    $(card).find('.card-front').addClass('offline-indicator');
});

const MAIN_URL = `http://${document.domain}:${location.port}`;

const deleteCheck = (context) => {
    const card = $(context).closest(".flip-card-container");
    const checkId = card.attr('itemid');
    fetch(`${MAIN_URL}/checks`, {
        method: 'DELETE',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({checkId})
    })
        .then(res => {
            if (res.ok) {
                card.remove();
            }
        });
}

const updateSetNumber = (context) => {
    const card = $(context).closest(".flip-card-container");
    const checkId = card.attr('itemid');
    const setId = $(context).val();

    fetch(`${MAIN_URL}/checks`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({checkId, setId})
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
const calibrateChecks = () => {
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