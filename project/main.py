# main.py
from flask import Blueprint, render_template, request, url_for, redirect, jsonify
from flask_login import login_required, current_user
from models import Carrier, Contact
from database import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/delete', methods=['POST'])
@login_required
def delete():
    contact_id = request.form.get('contact_id')
    print(contact_id)
    return redirect(url_for('main.contacts'))


@main.route('/test')
def test():
    # contact1 = Contact(name='Mary Davis', cell_number="405-277-0137", email='mary@gmail.com', carrier_id=2)
    # contact2 = Contact(name='John Doe', cell_number="253-327-4900", email='john@yahoo.com', carrier_id=3)
    # contact3 = Contact(name='Julie Drock', cell_number="617-694-0614", email='julie@gmail.com', carrier_id=2)
    # # carrier2 = Carrier(id=2, name='AT&T', email='@txt.att.net')
    # # db.session.add(contact)
    # db.session.bulk_save_objects([contact1, contact2, contact3])
    # db.session.commit()
    return render_template('index.html')


@main.route('/contacts', methods=['POST', 'GET'])
@login_required
def contacts():
    if request.method == 'GET':
        carriers = [carrier.as_dict() for carrier in Carrier.query.all()]
        contacts = [contact.as_dict() for contact in Contact.query.all()]
        return render_template('contacts.html', contacts=contacts, carriers=carriers)

    else:
        print(request)
