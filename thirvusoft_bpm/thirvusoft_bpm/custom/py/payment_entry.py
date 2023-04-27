import frappe
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
from frappe.core.doctype.communication.email import get_attach_link
import requests

@frappe.whitelist()
def send_message_confirmation(doc,event):
    for ref in doc.references:
        if ref.reference_doctype == 'Fees' and ref.reference_name and frappe.db.get_single_value('Whatsapp Settings','enable') == 1:
            message  = frappe.db.get_value('Payment Gateway Account',{'company':doc.company,'is_default':1},'confirmation_message')
            context = {
                'doc':doc
            }
            
            html = frappe.render_template(message, context)
            v=(" ".join("".join(re.sub("\<[^>]*\>", "<br>",html ).split("<br>")).split(' ') ))
            encoded_s = quote(v)

            guardians=frappe.db.sql(""" select phone_number from `tabStudent Guardian` md where enable_whatsapp_message = 1 and parent='{0}'""".format(doc.party),as_dict=1)
            instance_id =  frappe.db.get_single_value('Whatsapp Settings','instance_id')
            access_token =  frappe.db.get_single_value('Whatsapp Settings','access_token')
            default_print_format = frappe.db.get_value(
                    "Property Setter",
                    dict(property="default_print_format", doc_type=doc.doctype),
                    "value",
                )
            for i in guardians:
                link = get_attach_link(ref,default_print_format)
                soup = BeautifulSoup(link, 'html.parser')               
                urls = [link.get('href') for link in soup.find_all('a')]
                if urls and i["phone_number"]:
                    mobile_number = i["phone_number"].replace("+", "")
                    url = f'https://app.botsender.in/api/send.php?number={mobile_number}&type=media&message={encoded_s}&media_url={urls[0]}&instance_id={instance_id}&access_token={access_token}'
                    payload={}
                    headers = {}
                    response = requests.request("POST", url, headers=headers, data=payload)
