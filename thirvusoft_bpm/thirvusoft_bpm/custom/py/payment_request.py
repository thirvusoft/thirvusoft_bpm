import frappe
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest
def get_advance_entries(doc,event):
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

    #Non Payment Message
    if doc.grand_total <= 0 and doc.payment_gateway_account:
        doc.message = frappe.db.get_value('Payment Gateway Account',doc.payment_gateway_account,'non_payment_message')

def timesheet_whatsapp(doc,event):
    html = PaymentRequest.get_message(doc)
    v=(" ".join("".join(re.sub("\<[^>]*\>", "<br>",html ).split("<br>")).split(' ') ))
    v = v.replace('click here to pay', f'click here to pay: {doc.payment_url}')
    encoded_s = quote(v)

    guardians=frappe.db.sql(""" select phone_number from `tabStudent Guardian` md where enable_whatsapp_message = 1 and parent='{0}'""".format(doc.party),as_dict=1)
    
    for i in guardians:
        mobile_number=i["phone_number"]
        url = f"https://app.botsender.in/api/send.php?number=91{mobile_number}&type=text&message={encoded_s}&instance_id=64216E4885A3F&access_token=f7faedf4fcbacf627f9dd87c621785bb"
        payload={}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload)