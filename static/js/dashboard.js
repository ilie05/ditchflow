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
    if (!confirm("Are you sure you want to Start?")) return;

    fetch(`${MAIN_URL}/startAutorun`, {
        method: 'GET',
        headers: {
            'Authorization': jwtToken,
        },
    })
        .then(res => {
            if (res.ok) {
                $('#startBtn').prop('disabled', true);
                $('#stopBtn').prop('disabled', false);
                $('#pauseBtn').prop('disabled', false)
                $('.run-time .cont-display').show();
                countUpFromTime.interval = NaN;
                runTimePrep('0:0:0');
                $('.run-time .cont-hide').hide();
            }
        });
}

function stopSystem() {
    if (!confirm("Are you sure you want to Stop?")) return;

    fetch(`${MAIN_URL}/stopAutorun`, {
        method: 'GET',
        headers: {
            'Authorization': jwtToken,
        },
    })
        .then(res => {
            if (res.ok) {
                $('#startBtn').prop('disabled', false);
                $('#stopBtn').prop('disabled', true);
                $('#pauseBtn').text("Pause");
                $('#pauseBtn').prop('disabled', true);
                countUpFromTime.interval = -1
                $('.run-time .cont-display').hide();
                $('.run-time .cont-hide').show();
            }
        });

}

function pauseSystem() {
    if (!confirm(`Are you sure you want to ${$('#pauseBtn').text().trim()}?`)) return;

    fetch(`${MAIN_URL}/pauseAutorun`, {
        method: 'GET',
        headers: {
            'Authorization': jwtToken,
        },
    })
        .then(res => {
            if (res.ok) {
                let state = $('#pauseBtn').text().trim();
                if (state === "Pause") $('#pauseBtn').text("Unpause");
                else $('#pauseBtn').text("Pause");
                $('#stopBtn').prop('disabled', false);
                $('#startBtn').prop('disabled', true);
            }
        });
}

function runTimePrep(run_time) {
    let dt = new Date();
    dt.setHours(Number(run_time.split(':')[0]));
    dt.setMinutes(Number(run_time.split(':')[1]));
    dt.setSeconds(Number(run_time.split(':')[2]));
    countUpFromTime(dt);
}

function countUpFromTime(countFrom) {
    let now = new Date();
    now.setSeconds(0);
    now.setMinutes(0);
    now.setHours(0);
    let timeDifference = (countFrom - now);

    let secondsInADay = 60 * 60 * 1000 * 24,
        secondsInAHour = 60 * 60 * 1000;

    let hours = Math.floor((timeDifference % (secondsInADay)) / (secondsInAHour) * 1);
    let mins = Math.floor(((timeDifference % (secondsInADay)) % (secondsInAHour)) / (60 * 1000) * 1);
    let secs = Math.floor((((timeDifference % (secondsInADay)) % (secondsInAHour)) % (60 * 1000)) / 1000 * 1);

    $('.run-time .h').text(hours);
    $('.run-time .m').text(mins);
    $('.run-time .s').text(secs);

    countFrom.setSeconds(countFrom.getSeconds() + 1);
    if (countUpFromTime.interval === -1) return;
    clearTimeout(countUpFromTime.interval);
    countUpFromTime.interval = setTimeout(function () {
        countUpFromTime(countFrom);
    }, 1000);
}