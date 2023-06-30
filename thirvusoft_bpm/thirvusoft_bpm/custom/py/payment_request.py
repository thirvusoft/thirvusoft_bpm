import frappe
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest
from frappe.core.doctype.communication.email import get_attach_link
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file


def get_advance_entries(doc,event):
    # if doc.party_type == "Student" and doc.party and frappe.db.get_value('Student',doc.party,'virtual_account'):
    #     doc.virtual_account  = frappe.db.get_value('Student',doc.party,'virtual_account')
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
        if doc.grand_total > 0 and frappe.db.get_value('Company',fees.company,'charges_applicable') and not doc.without_charges:
            doc.without_charges = doc.grand_total
            doc.grand_total =  ( doc.without_charges * (frappe.db.get_value('Company',fees.company,'razorpay_charges')/100)) + doc.without_charges
        elif doc.grand_total > 0 and not frappe.db.get_value('Company',fees.company,'charges_applicable') and doc.without_charges:
            doc.grand_total =  doc.without_charges
        #Non Payment Message
        if doc.grand_total <= 0 and doc.payment_gateway_account:
            doc.message = frappe.db.get_value('Payment Gateway Account',doc.payment_gateway_account,'non_payment_message')

def whatsapp_message(doc,event):
    if frappe.db.get_single_value('Whatsapp Settings','enable') == 1 and doc.reference_doctype == 'Fees' and doc.reference_name:
        html = PaymentRequest.get_message(doc)
        v=(" ".join("".join(re.sub("\<[^>]*\>", "<br>",html ).split("<br>")).split(' ') ))
        v = v.replace('click here to pay', f'click here to pay: {doc.payment_url}')
        encoded_s = quote(v)

        guardians=frappe.db.sql(""" select phone_number,guardian_name from `tabStudent Guardian` md where enable_whatsapp_message = 1 and parent='{0}'""".format(doc.party),as_dict=1)
        instance_id =  frappe.db.get_single_value('Whatsapp Settings','instance_id')
        access_token =  frappe.db.get_single_value('Whatsapp Settings','access_token')
        company = frappe.get_value('Fees',doc.reference_name,'company')

        for i in guardians:
            def_message  = frappe.db.get_value('Payment Gateway Account',{'company':company,'is_default':1},'default_header_for_whatsapp_mail_message')
            def_context = {
                'doc':frappe.get_doc('Student',doc.party),
                'guardian':i['guardian_name']
            }
                
            html2 = frappe.render_template(def_message, def_context)
            def_v =(" ".join("".join(re.sub("\<[^>]*\>", "<br>",html2 ).split("<br>")).split(' ') ))


            fees_doc  = frappe.get_doc('Fees',doc.reference_name)
            pdf_bytes = frappe.get_print(doc.reference_doctype, doc.reference_name, doc=fees_doc, print_format=doc.print_format)
            pdf_name = doc.reference_name + '.pdf'
            pdf_url = frappe.utils.file_manager.save_file(pdf_name, get_pdf(pdf_bytes), doc.doctype, doc.name)           
            urls = f'{frappe.utils.get_url()}{pdf_url.file_url}'
            try:
                if urls and i["phone_number"]:
                    mobile_number = i["phone_number"].replace("+", "")
                    url = f'https://app.botsender.in/api/send?number=91{mobile_number}&type=media&message={def_v+encoded_s}&media_url={urls}&filename={pdf_name}&instance_id={instance_id}&access_token={access_token}'
                    payload={}
                    headers = {}
                    response = requests.request("GET", url, headers=headers, data=payload)
                    #frappe.printerr(response.__dict__)
                    frappe.log_error(title='error msg', message=response.__dict__)
                    frappe.delete_doc('File',pdf_url.name)
                    doc = frappe.new_doc("Whatsapp Log")
                    doc.update({
                        "mobile_no": mobile_number,
                        
                        "status":"Success",
                        "payload": f"{url}",
                        "response" : response,
                        "last_execution": frappe.utils.now()
                    })
                    doc.flags.ignore_permissions = True
                    doc.flags.ignore_mandatory = True
                    doc.insert()
                    frappe.delete_doc('File',pdf_url.name)
            except Exception as e:
                if urls and i["phone_number"]:
                    mobile_number = i["phone_number"].replace("+", "")
                    url = f'https://app.botsender.in/api/send?number=91{mobile_number}&type=media&message={def_v+encoded_s}&media_url={urls}&filename={pdf_name}&instance_id={instance_id}&access_token={access_token}'
                    payload={}
                    headers = {}
                    doc = frappe.new_doc("Whatsapp Log")
                    doc.update({
                        "mobile_no": mobile_number,
                        
                        "status":"Failed",
                        "payload": f"{url}",
                        "response" : e,
                        "last_execution": frappe.utils.now()
                    })
                    doc.flags.ignore_permissions = True
                    doc.flags.ignore_mandatory = True
                    doc.insert()
                    frappe.delete_doc('File',pdf_url.name)