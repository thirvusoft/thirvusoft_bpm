import frappe
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest
from frappe.core.doctype.communication.email import get_attach_link
from frappe.utils.pdf import get_pdf

def get_advance_entries(doc,event):
    if doc.party_type == "Student" and doc.party and frappe.db.get_value('Student',doc.party,'virtual_account'):
        doc.virtual_account  = frappe.db.get_value('Student',doc.party,'virtual_account')
    
    if doc.reference_doctype == 'Fees' and doc.reference_name:
        fees = frappe.get_doc('Fees',doc.reference_name)
        gl_entry = frappe.get_all('GL Entry',{'debit':['>',0],'is_cancelled':0,'credit':0,'party_type':doc.party_type,'party':doc.party,'against_voucher':doc.reference_name,'voucher_no':['!=',doc.reference_name]},['account','debit'])
        doc.advance_payments = []
        doc.total_advance_payment = 0
        fees.advance_payments = []
        fees.total_advance_payment = 0
        for entry in gl_entry:
            doc.append('advance_payments',{
                'account':entry['account'],
                'amount':entry['debit']
            })
            fees.append('advance_payments',{
                'account':entry['account'],
                'amount':entry['debit']
            })
            doc.total_advance_payment += entry['debit']
            fees.total_advance_payment += entry['debit']
        fees.save()

        #1.5 discount percentage
        if doc.grand_total > 0 and frappe.db.get_value('Company',fees.company,'charges_applicable'):
            doc.grand_total =  (doc.grand_total * (frappe.db.get_value('Company',fees.company,'razorpay_charges')/100)) + doc.grand_total
        #Non Payment Message
        if doc.grand_total <= 0 and doc.payment_gateway_account:
            doc.message = frappe.db.get_value('Payment Gateway Account',doc.payment_gateway_account,'non_payment_message')

def whatsapp_message(doc,event):
    if frappe.db.get_single_value('Whatsapp Settings','enable') == 1:
        html = PaymentRequest.get_message(doc)
        v=(" ".join("".join(re.sub("\<[^>]*\>", "<br>",html ).split("<br>")).split(' ') ))
        v = v.replace('click here to pay', f'click here to pay: {doc.payment_url}')
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
