const MAIN_URL = `http://${document.domain}:${location.port}`;
const TIME_INTERVAL = 3000;
let INTERVAL;


const updateValvePreflow = (context, vName) => {
    const valveId = $(context).parent().attr('valve-id');
    const preflow = $(context).val();
    if (preflow === '' || Number(preflow) < 0 || Number(preflow) > 100) return;

    fetch(`${MAIN_URL}/preflow`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({valveId, preflow})
    })
        .then(res => {
            const message = `Preflow for valve ${vName} has been updated!`;
            updateMessageCallback(res, message);
        });
}

const updateValveRun = (context, vName) => {
    const valveId = $(context).parent().attr('valve-id');
    const valveRun = $(context).val();
    if (valveRun === '' || Number(valveRun) < 0 || Number(valveRun) > 100) return;

    fetch(`${MAIN_URL}/valveRun`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({valveId, valveRun})
    })
        .then(res => {
            const message = `Run for valve ${vName} has been updated!`;
            updateMessageCallback(res, message);
        });
}

const updateSensorDelay = (context, sName) => {
    const sensorId = $(context).parent().attr('sensor-id');
    const delay = $(context).val();
    if (delay === '' || Number(delay) < 0) return;

    fetch(`${MAIN_URL}/delay`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({sensorId, delay})
    })
        .then(res => {
            const message = `Delay for sensor ${sName} has been updated!`;
            updateMessageCallback(res, message);
        });
}

const updateLandAutorun = (context, lNumber) => {
    const landId = $(context).closest('.set-container').attr('land-id');
    const isChecked = $(context).is(":checked");

    fetch(`${MAIN_URL}/autorun`, {
        method: 'POST',
        headers: {
            'Authorization': jwtToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({landId, isChecked})
    })
        .then(res => {
            const message = `Autorun for land ${lNumber} is ${isChecked ? 'ON' : 'OFF'}!`;
            updateMessageCallback(res, message);
        });
}

const deleteSet = (context) => {
    const setId = $(context).closest('.set-container').attr('set-id');
    const landId = $(context).closest('.set-container').attr('land-id');

    fetch(`${MAIN_URL}/configuration`, {
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