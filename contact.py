from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_required
from models import Carrier, Contact
from database import db
import json
from utils import format_phone_number, remove_tags

contact = Blueprint('contact', __name__)


@contact.route('/delete', methods=['POST'])
@login_required
def delete():
    contact_id = request.form.get('contact_id')
    Contact.query.filter_by(id=contact_id).delete()
    db.session.commit()
    return redirect(url_for('contact.contacts'))


@contact.route('/create', methods=['POST'])
@login_required
def create():
    contacts = json.loads(request.form.get('contacts'))
    for contact in contacts:
        db_contact = Contact.query.filter_by(id=contact['id']).first()
        if db_contact:
            db_contact.name = remove_tags(contact['name'])
            db_contact.email = remove_tags(contact['email'])
            db_contact.cell_number = format_phone_number(contact['cell_number'])
            db_contact.carrier_id = contact['carrier_id']
            db_contact.notify = contact['notify']
        else:
            new_contact = Contact(name=remove_tags(contact['name']), email=remove_tags(contact['email']),
                                  cell_number=format_phone_number(contact['cell_number']),
                                  carrier_id=contact['carrier_id'], notify=contact['notify'])
            db.session.add(new_contact)
        db.session.commit()
    return redirect(url_for('contact.contacts'))


@contact.route('/contacts', methods=['POST', 'GET'])
@login_required
def contacts():
    if request.method == 'GET':
        carriers = [carrier.as_dict() for carrier in Carrier.query.all()]
        contacts = [contact.as_dict() for contact in Contact.query.all()]
        return render_template('contacts.html', contacts=contacts, carriers=carriers)

    else:
        print(request)
