const source1 = new EventSource("/sensor_notification");

source1.onmessage = function (event) {
    const data = JSON.parse(event.data);
    console.log(data);
    let card = $(`.cards-container [itemid=${data.id}]`);
    if (!card.length) return;

    $(card).find('li.sName').text(`Sensor Name: ${data.name}`);
    $(card).find('li.sWater').text(`Water Level: ${data.water} inches`);
    $(card).find('li.sBattery').text(`Battery Voltage: ${data.battery} V`);
    $(card).find('li.sTemperature').text(`Temperature: ${data.temperature} °F`);
    $(card).find('li.sFloat').text(`Float: ${data.float ? 'UP' : 'DOWN'}`);
    $(card).find('li.sLastSeen').text(`Last seen: ${data.last_update}`);

    $(card).find('.card-front').removeClass('offline-indicator');
}

const source2 = new EventSource("/goOffline");
source2.onmessage = function (event) {
    const id = JSON.parse(event.data);
    console.log(id);
    let card = $(`.cards-container [itemid=${id}]`);
    if (!card.length) return;

    $(card).find('li.sStatus').text('Status: OFFLINE');
    $(card).find('li.sWater').text('Water Level: ---');
    $(card).find('li.sBattery').text('Battery Voltage: ---');
    $(card).find('li.sTemperature').text('Temperature: ---');
    $(card).find('li.sFloat').text('Float: ---');

    $(card).find('.card-front').addClass('offline-indicator');
}
