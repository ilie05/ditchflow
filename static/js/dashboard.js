const MAIN_URL = `http://${document.domain}:${location.port}`;

function sendPosition(select, t) {
    let position = $(select).val(), objId;
    console.log("Option Chosen by you is " + position);

    if (t === 'v') objId = $(select).attr('valve-id')
    else if (t === 'c') objId = $(select).attr('check-id')


    fetch(`${MAIN_URL}/sendPosition`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({objId, position, t})
    })
        .then(res => {
            if (res.ok) console.log("position sent")
        });
}

function displayPosition(select) {
    const position = $(select).val();
    $(select).parent().find('.slider-position').text(position);
}

const socket = io(`http://${document.domain}:${location.port}/notification`);
socket.on('connect', function () {
    console.log("Connected")
});

socket.on('valve_notification', function (data) {
    console.log(data);
    let card = $(`[valve-id=${data.id}]`);
    if (!card.length) return;

    $(card).find('td.vName').text(data.name);
    $(card).find('td.vActuatorStatus').text(data.actuator_status);
    $(card).find('td.vBattery').text(`${data.battery} V`);
    $(card).find('td.vTemperature').text(`${data.temperature} °F`);

    if (data.actuator_status === 'Moving') {
        $(card).find('td.vActuatorActualPosition').text(`---`);
    } else {
        $(card).find('td.vActuatorActualPosition').text(`${data.actuator_position}%`);
        $(`[valve_config-id=${data.id}]`).val(data.actuator_position);
    }
});

socket.on('check_notification', function (data) {
    console.log(data);
    let card = $(`[check-id=${data.id}]`);
    if (!card.length) return;

    $(card).find('td.cName').text(data.name);
    $(card).find('td.cActuatorStatus').text(data.actuator_status);
    $(card).find('td.cBattery').text(`${data.battery} V`);
    $(card).find('td.cTemperature').text(`${data.temperature} °F`);

    if (data.actuator_status === 'Moving') {
        $(card).find('td.cActuatorActualPosition').text(`---`);
    } else {
        $(card).find('td.cActuatorActualPosition').text(`${data.actuator_position}%`);
        $(`[check_config-id=${data.id}]`).val(data.actuator_position);
    }
});

socket.on('sensor_notification', function (data) {
    console.log(data);
    let card = $(`[sensor-id=${data.id}]`);
    if (!card.length) return;

    if (data.float) card.css('background-color', 'forestgreen');
    else card.css('background-color', 'dimgray')
});

function startSystem() {
    if (confirm("Are you sure you want to start?")) console.log("da")
    else console.log("no")
}

function stopSystem() {
    if (confirm("Are you sure you want to stop?")) console.log("da")
    else console.log("no")
}

function pauseSystem() {
    if (confirm("Are you sure you want to pause?")) console.log("da")
    else console.log("no")
}