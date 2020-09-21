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
    if (position === '' || position === undefined || position === null || Number(position) < 0 || Number(position) > 100){
        return;
    }
    console.log((position));
}
