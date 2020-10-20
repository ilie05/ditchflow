const MAIN_URL = `http://${document.domain}:${location.port}`;

const updateValvePreflow = (context) => {
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
            if (res.ok) {
                console.log("BUN");
            }
        });
}

const updateValveRun = (context) => {
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
            if (res.ok) {
                console.log("BUN");
            }
        });
}

const updateSensorDelay = (context) => {
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
            if (res.ok) {
                console.log("BUN");
            }
        });
}

