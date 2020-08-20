# contact.py
from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_required
from models import Carrier, Contact
from database import db
import json

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
            db_contact.name = contact['name']
            db_contact.email = contact['email']
            db_contact.cell_number = contact['cell_number']
            db_contact.carrier_id = contact['carrier_id']
            db_contact.notify = contact['notify']
        else:
            new_contact = Contact(name=contact['name'], email=contact['email'],
                                  cell_number=contact['cell_number'], carrier_id=contact['carrier_id'])
            db.session.add(new_contact)
        db.session.commit()
    return redirect(url_for('contact.contacts'))


@contact.route('/test')
def test():
    contact1 = Contact(name='Nero Brone', cell_number="453-231-017", email='tony@gmail.com', carrier_id=2)
    # contact2 = Contact(name='John Doe', cell_number="253-327-4900", email='john@yahoo.com', carrier_id=3)
    # contact3 = Contact(name='Julie Drock', cell_number="617-694-0614", email='julie@gmail.com', carrier_id=2)
    # # carrier2 = Carrier(id=2, name='AT&T', email='@txt.att.net')
    # db.session.bulk_save_objects([contact1, contact2, contact3])
    # db.session.add(contact1)
    # db.session.commit()
    return render_template('index.html')


@contact.route('/contacts', methods=['POST', 'GET'])
@login_required
def contacts():
    if request.method == 'GET':
        carriers = [carrier.as_dict() for carrier in Carrier.query.all()]
        contacts = [contact.as_dict() for contact in Contact.query.all()]
        return render_template('contacts.html', contacts=contacts, carriers=carriers)

    else:
        print(request)
