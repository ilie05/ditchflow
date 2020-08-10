# main.py
from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_required, current_user

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


@main.route('/contacts', methods=['POST', 'GET'])
@login_required
def contacts():
    if request.method == 'GET':
        contacts = [
            {"id": 1, "name": "Code Moore", "cell": "812-518-5056", "email": "mark@codewithmark.com", "carrier_id": 3},
            {"id": 2, "name": "Mary Davis", "cell": "405-277-0137", "email": "mary@gmail.com", "carrier_id": 2},
            {"id": 3, "name": "John Doe", "cell": "253-327-4900", "email": "john@yahoo.com", "carrier_id": 1},
            {"id": 4, "name": "Julie Drock", "cell": "617-694-0614", "email": "julie@gmail.com", "carrier_id": 3},
        ]
        carriers = [
            {"id": 1, "name": "T-Mobile", "email": "@tmomail.net"},
            {"id": 2, "name": "Verizon", "email": "@vtext.com"},
            {"id": 3, "name": "AT&T", "email": "@txt.att.net"},
        ]
        return render_template('contacts.html', contacts=contacts, carriers=carriers)

    else:
        print(request)
