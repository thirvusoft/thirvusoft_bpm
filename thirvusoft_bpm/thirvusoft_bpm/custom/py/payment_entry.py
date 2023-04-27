import frappe
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
from frappe.core.doctype.communication.email import get_attach_link
import requests
from frappe.utils.file_manager import save_file
from frappe.utils.pdf import get_pdf

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
                pdf_bytes = frappe.get_print(doc.doctype, doc.name, doc=doc, print_format=default_print_format)
                pdf_name = doc.name + '.pdf'
                pdf_url = frappe.utils.file_manager.save_file(pdf_name, get_pdf(pdf_bytes), doc.doctype, doc.name)           
                urls = f'{frappe.utils.get_url()}{pdf_url.file_url}'
                if urls and i["phone_number"]:
                    mobile_number = i["phone_number"].replace("+", "")
                    url = f'https://app.botsender.in/api/send.php?number={mobile_number}&type=media&message={encoded_s}&media_url={urls}&instance_id={instance_id}&access_token={access_token}'
                    payload={}
                    headers = {}
                    response = requests.request("POST", url, headers=headers, data=payload)
                    frappe.delete_doc('File',pdf_url.name)