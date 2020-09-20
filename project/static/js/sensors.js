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
                $(card).find('.card-error').hide();
            } else {
                if (res.status === 409) {
                    // land number already exists
                    $(card).find('.card-error').show();
                }
            }
        });
}