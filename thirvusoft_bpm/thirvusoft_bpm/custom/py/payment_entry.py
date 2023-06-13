import frappe
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
from frappe.core.doctype.communication.email import get_attach_link
import requests
from frappe.utils.file_manager import save_file
from frappe.utils.pdf import get_pdf
from frappe.utils.background_jobs import enqueue

@frappe.whitelist()
def send_message_confirmation(doc,event):
    for ref in doc.references:
        if ref.reference_doctype == 'Fees' and ref.reference_name and frappe.db.get_single_value('Whatsapp Settings','enable') == 1 and frappe.db.get_value('Company',doc.company,'enable_payment_confirmation_message') ==1:
            def_v = ''
            encoded_s = ''
            fees_doc = frappe.get_doc('Fees',ref.reference_name)

            message  = frappe.db.get_value('Payment Gateway Account',{'company':doc.company,'is_default':1},'confirmation_message')
            if message:
                context = {
                    'doc':doc
                }
                
                html = frappe.render_template(message, context)
                v=(" ".join("".join(re.sub("\<[^>]*\>", "<br>",html ).split("<br>")).split(' ') ))
                encoded_s = quote(v)

            guardians=frappe.db.sql(""" select phone_number,guardian_name from `tabStudent Guardian` md where enable_whatsapp_message = 1 and parent='{0}'""".format(doc.party),as_dict=1)
            instance_id =  frappe.db.get_single_value('Whatsapp Settings','instance_id')
            access_token =  frappe.db.get_single_value('Whatsapp Settings','access_token')
            default_print_format = frappe.db.get_value(
                    "Property Setter",
                    dict(property="default_print_format", doc_type=doc.doctype),
                    "value",
                )
            for i in guardians:
                def_message  = frappe.db.get_value('Payment Gateway Account',{'company':fees_doc.company,'is_default':1},'default_header_for_whatsapp_mail_message')
                if def_message:
                    def_context = {
                        'doc':frappe.get_doc('Student',fees_doc.student),
                        'guardian':i['guardian_name']
                    }
                        
                    html2 = frappe.render_template(def_message, def_context)
                    def_v =(" ".join("".join(re.sub("\<[^>]*\>", "<br>",html2 ).split("<br>")).split(' ') ))

                pdf_bytes = frappe.get_print(doc.doctype, doc.name, doc=doc, print_format=default_print_format)
                pdf_name = doc.name + '.pdf'
                pdf_url = frappe.utils.file_manager.save_file(pdf_name, get_pdf(pdf_bytes), doc.doctype, doc.name)           
                urls = f'{frappe.utils.get_url()}{pdf_url.file_url}'
                if urls and i["phone_number"]:
                    mobile_number = i["phone_number"].replace("+", "")
                    frappe.errprint(mobile_number)
                    url = f'https://app.botsender.in/api/send?number=91{mobile_number}&type=media&message={def_v + encoded_s}&media_url={urls}&filename={pdf_name}&instance_id={instance_id}&access_token={access_token}'
                    payload={}
                    headers = {}
                    response = requests.request("POST", url, headers=headers, data=payload)
                    frappe.delete_doc('File',pdf_url.name)


            """send email with payment link"""
            email_args = {
                "recipients": fees_doc.student_email,
                "sender": None,
                "subject": f'Payment Entry for {doc.name}',
                "message": def_v + encoded_s,
                "now": True,
                "attachments": [
                    frappe.attach_print(
                        doc.doctype,
                        doc.name,
                        file_name=doc.name,
                        print_format=default_print_format,
                    )
                ],
            }
            enqueue(method=frappe.sendmail, queue="short", timeout=300, is_async=True, **email_args)