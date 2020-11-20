function sendPosition(select) {
    const position = $(select).val();
    console.log("Option Chosen by you is " + position);
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
    }
});

socket.on('sensor_notification', function (data) {
    console.log(data);
    let card = $(`[sensor-id=${data.id}]`);
    if (!card.length) return;

    if (data.float) card.css('background-color', 'forestgreen');
    else card.css('background-color', 'dimgray')
});