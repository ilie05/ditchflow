const trashIcon = '<svg width="2em" height="2em" viewBox="0 0 16 16" class="bi bi-trash" fill="currentColor" xmlns="http://www.w3.org/2000/svg">\n' +
    '                <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>\n' +
    '                <path fill-rule="evenodd"\n' +
    '                      d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4L4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>\n' +
    '            </svg>'

const onRowDataClick = function (event) {
    var row_div = $(this);
    var col_name = row_div.attr('col_name');
    if (col_name === 'carrier' || col_name === 'notify' || col_name === 'delete') return;

    event.preventDefault();

    //make div editable
    $(this).closest('div').attr('contenteditable', 'true');
    //add bg css
    $(this).addClass('bg-warning').css('padding', '0 5px');

    $(this).focus();
}

const onToggle = function (e) {
    const toggle = e.target;
    const row_div = $(toggle).closest('.row_data');
    var row_id = row_div.closest('tr').attr('row_id');
    console.log(row_id);
}

const removeLine = function (context){
    $(context).closest('tr').remove();
}

$(document).ready(function ($) {
    var tbl = '';
    //--->create table body rows > start
    $.each(contacts, function (index, contact) {
        tbl += `<tr row_id="${contact['id']}">`;
        tbl += `<td ><div class="row_data" col_name="name">${contact['name']}</div></td>`;
        tbl += `<td ><div class="row_data" col_name="email">${contact['email']}</div></td>`;
        tbl += `<td ><div class="row_data" col_name="cell">${contact['cell']}</div></td>`;
        tbl += `<td ><div class="row_data" col_name="carrier">`;

        tbl += '<select class="selectpicker show-tick" data-style="btn-info">\n';
        $.each(carriers, function (index, carrier) {
            let selected = carrier.id === contact['carrier_id'];
            if (selected) {
                tbl += `<option selected>${carrier.name}</option>`;
            } else {
                tbl += `<option>${carrier.name}</option>`;
            }
        });
        tbl += '<select/></div></td>';

        tbl += '<td ><div class="row_data" col_name="notify">';
        tbl += '<label class="switch">\n' +
            '            <input type="checkbox">\n' +
            '            <div class="slider"></div>\n' +
            '        </label>';
        tbl += '</div></td>';

        tbl += '<td ><div class="row_data" col_name="delete">';
        tbl += '<form action="/delete" method="post">\n' +
            `     <input name="contact_id" value="${contact['id']}" hidden/>\n` +
            '     <button type="submit" class="btn btn-default btn-sm">\n' + trashIcon +
            '     </button>\n' +
            '    </form>';
        tbl += '</div></td>';

        tbl += '</tr>';
    });
    //--->create table body rows > end
    $(document).find('.tbl_user_data table tbody').html(tbl);

    $("input[type='checkbox']").change(onToggle);
    $(document).on('click', '.row_data', onRowDataClick)

    //--->add new contact > start
    $(document).on('click', '.add_contact', function (event) {
        let last_row = $('.tbl_user_data table tr:last'), tbl = '';
        let row_id = Math.random().toString(36).substring(2);

        tbl += `<tr class="new_row" row_id="${row_id}">`;
        tbl += `<td ><div class="row_data editable" col_name="name"></div></td>`;
        tbl += `<td ><div class="row_data editable" col_name="email"></div></td>`;
        tbl += `<td ><div class="row_data editable" col_name="cell"></div></td>`;
        tbl += `<td ><div class="row_data" col_name="carrier">`;

        tbl += '<select class="selectpicker show-tick" data-style="btn-info">\n';
        $.each(carriers, function (index, carrier) {
            tbl += `<option>${carrier.name}</option>`;
        });
        tbl += '<select/></div></td>';

        tbl += '<td ><div class="row_data" col_name="notify">';
        tbl += '<label class="switch">\n' +
            '            <input type="checkbox">\n' +
            '            <div class="slider"></div>\n' +
            '        </label>';
        tbl += '</div></td>';

        tbl += '<td ><div class="row_data" col_name="delete">';
        tbl += '<button type="submit" class="btn btn-default btn-sm" onclick="removeLine(this)">\n' + trashIcon +
            '      </button>\n';
        tbl += '</div></td>';

        tbl += '</tr>';


        last_row.after(tbl);
        $('.row_data', tbl).on('click', onRowDataClick);
        $('.selectpicker:last').selectpicker('refresh');
        $('input[type="checkbox"]:last').change(onToggle);
    })
    //--->add new contact > end

    //--->save single field data > start
    $(document).on('focusout', '.row_data', function (event) {
        event.preventDefault();

        var row_id = $(this).closest('tr').attr('row_id');

        var row_div = $(this)
            .removeClass('bg-warning') //add bg css
            .css('padding', '')

        var col_name = row_div.attr('col_name');
        var col_val = row_div.html();

        // var arr = {};
        // arr[col_name] = col_val;
        //
        // //use the "arr"	object for your ajax call
        // $.extend(arr, {row_id: row_id});
        //
        // //out put to show
        // $('.post_msg').html('<pre class="bg-success">' + JSON.stringify(arr, null, 2) + '</pre>');

    })
    //--->save single field data > end


    //--->button > edit > start
    // $(document).on('click', '.btn_edit', function (event) {
    //     event.preventDefault();
    //     var tbl_row = $(this).closest('tr');
    //
    //     var row_id = tbl_row.attr('row_id');
    //
    //     tbl_row.find('.btn_save').show();
    //     tbl_row.find('.btn_cancel').show();
    //
    //     //hide edit button
    //     tbl_row.find('.btn_edit').hide();
    //
    //     //make the whole row editable
    //     tbl_row.find('.row_data')
    //         .attr('contenteditable', 'true')
    //         .attr('edit_type', 'button')
    //         .addClass('bg-warning')
    //         .css('padding', '3px')
    //
    //     //--->add the original entry > start
    //     tbl_row.find('.row_data').each(function (index, val) {
    //         //this will help in case user decided to click on cancel button
    //         $(this).attr('original_entry', $(this).html());
    //     });
    //     //--->add the original entry > end
    //
    // });
    //--->button > edit > end


    //--->button > cancel > start
    // $(document).on('click', '.btn_cancel', function (event) {
    //     event.preventDefault();
    //
    //     var tbl_row = $(this).closest('tr');
    //
    //     var row_id = tbl_row.attr('row_id');
    //
    //     //hide save and cacel buttons
    //     tbl_row.find('.btn_save').hide();
    //     tbl_row.find('.btn_cancel').hide();
    //
    //     //show edit button
    //     tbl_row.find('.btn_edit').show();
    //
    //     //make the whole row editable
    //     tbl_row.find('.row_data')
    //         .attr('edit_type', 'click')
    //         .removeClass('bg-warning')
    //         .css('padding', '')
    //
    //     tbl_row.find('.row_data').each(function (index, val) {
    //         $(this).html($(this).attr('original_entry'));
    //     });
    // });
    //--->button > cancel > end


    //--->save whole row entery > start
    // $(document).on('click', '.btn_save', function (event) {
    //     event.preventDefault();
    //     var tbl_row = $(this).closest('tr');
    //
    //     var row_id = tbl_row.attr('row_id');
    //
    //
    //     //hide save and cacel buttons
    //     tbl_row.find('.btn_save').hide();
    //     tbl_row.find('.btn_cancel').hide();
    //
    //     //show edit button
    //     tbl_row.find('.btn_edit').show();
    //
    //
    //     //make the whole row editable
    //     tbl_row.find('.row_data')
    //         .attr('edit_type', 'click')
    //         .removeClass('bg-warning')
    //         .css('padding', '')
    //
    //     //--->get row data > start
    //     var arr = {};
    //     tbl_row.find('.row_data').each(function (index, val) {
    //         var col_name = $(this).attr('col_name');
    //         var col_val = $(this).html();
    //         arr[col_name] = col_val;
    //     });
    //     //--->get row data > end
    //
    //     //use the "arr"	object for your ajax call
    //     $.extend(arr, {row_id: row_id});
    //
    //     //out put to show
    //     $('.post_msg').html('<pre class="bg-success">' + JSON.stringify(arr, null, 2) + '</pre>')
    //
    //
    // });
    //--->save whole row entery > end
});