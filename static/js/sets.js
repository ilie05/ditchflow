const MAIN_URL = `http://${document.domain}:${location.port}`;
const TIME_INTERVAL = 3000;
let INTERVAL;


const updateStartPreflow = (context, Name, t) => {
    let fieldVal = $(context).val(), objId;

    if (t === 'v') objId = $(context).parent().attr('valve-id');
    else if (t === 'c') objId = $(context).parent().attr('check-id');

    if (fieldVal === '' || Number(fieldVal) < 0 || Number(fieldVal) > 100) return;

    fetch(`${MAIN_URL}/startpreflow`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({objId, fieldVal, t})
    })
        .then(res => {
            const message = ` ${t === 'v' ? 'Preflow for valve' : 'Start for check'} ${Name} has been updated!`;
            updateMessageCallback(res, message);
        });
}

const updateRun = (context, Name, t) => {
    let run = $(context).val(), objId;
    if (t === 'v') objId = $(context).parent().attr('valve-id');
    else if (t === 'c') objId = $(context).parent().attr('check-id');
    if (run === '' || Number(run) < 0 || Number(run) > 100) return;

    fetch(`${MAIN_URL}/run`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({objId, run, t})
    })
        .then(res => {
            const message = `Run for ${t === 'v' ? 'valve' : 'check'} ${Name} has been updated!`;
            updateMessageCallback(res, message);
        });
}

const updateSensorDelay = (context, sName) => {
    const sensorConfigId = $(context).parent().attr('sensor_config-id');
    const delay = $(context).val();
    if (delay === '' || Number(delay) < 0) return;

    fetch(`${MAIN_URL}/delay`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({sensorConfigId, delay})
    })
        .then(res => {
            const message = `Delay for sensor ${sName} has been updated!`;
            updateMessageCallback(res, message);
        });
}

const updateAutorun = (context, Number, t) => {
    let isChecked = $(context).is(":checked"), objId;
    if (t === 'v') objId = $(context).closest('.set-container').attr('land-id');
    else if (t === 'c') objId = $(context).closest('.set-container').attr('set-id');

    fetch(`${MAIN_URL}/autorun`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({objId, isChecked, t})
    })
        .then(res => {
            const message = `Autorun for ${t === 'v' ? 'land' : 'set'} ${Number} is ${isChecked ? 'ON' : 'OFF'}!`;
            updateMessageCallback(res, message);
        });
}

const deleteSet = (context) => {
    const setId = $(context).closest('.set-container').attr('set-id');
    const landId = $(context).closest('.set-container').attr('land-id');

    fetch(`${MAIN_URL}/config_set`, {
        method: 'DELETE',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({setId, landId})
    })
        .then(res => {
            if (res.ok) {
                location.reload();
            }
        });
}

const updateMessageCallback = (res, message) => {
    const updateMessage = $('#update-message');
    if (res.status === 200) {
        updateMessage.text(message);
        updateMessage.show();
        clearInterval(INTERVAL);
        INTERVAL = setInterval(() => updateMessage.hide(), TIME_INTERVAL);
    }
}

const updateLandDelay = (context, landId) => {
    const delay = $(context).val();
    if (delay === '' || Number(delay) < 0) return;

    fetch(`${MAIN_URL}/landdelay`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({landId, delay})
    })
        .then(res => {
            const message = `Land delay has been updated!`;
            updateMessageCallback(res, message);
        });
}

const updateBeforeAfter = (context, objId, Name) => {
    let isChecked = $(context).is(":checked");

    fetch(`${MAIN_URL}/beforeafter`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({objId, isChecked})
    })
        .then(res => {
            const message = `Before/After for check ${Name} is ${isChecked ? 'ON' : 'OFF'}!`;
            updateMessageCallback(res, message);
        });
}

const changeConfig = (context) => {
    const config_name = $(context).val();
    window.location = `${MAIN_URL}/configuration?config_name=${config_name}`
}

const deleteConfig = () => {
    const config_name = $('#config_select').val();
    if (!config_name) return;
    fetch(`${MAIN_URL}/configuration`, {
        method: 'DELETE',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({config_name})
    })
        .then(res => {
            if (res.ok) {
                window.location = `${MAIN_URL}/configuration`
            }
        });
}