from flask import current_app
import telnyx
from models import Contact, Carrier

def send_sms(msg):

    telnyx.api_key = current_app.config.get("TELNYX_KEY")
    your_telnyx_number = current_app.config.get("TELNYX_NUMBER")
   

    contacts = Contact.query.filter_by(notify=True).all()
    for contact in contacts:
        
        destination_number = (f'+1{contact.cell_number}')
        
        telnyx.Message.create(from_=your_telnyx_number,to=destination_number,text=msg,)
    

    
