import frappe
import json
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request

@frappe.whitelist()

def trigger_bulk_message(list_of_docs):
    list_of_docs = json.loads(list_of_docs)
    frappe.enqueue(create_payment_request, list_of_docs = list_of_docs)
    frappe.msgprint("Payment Request Will Be Creating In Backgroud Within 20 Minutes.")

    
def create_payment_request(list_of_docs=None):
    update_dict = {}
    if list_of_docs:
        new_transaction = frappe.new_doc('Bulk Transaction Log')
        for fees in list_of_docs:
            
            new_transaction.append('bulk_transaction_log_table',{
                'fees':fees,
                'status':"Pending"
            })
            new_transaction.save()
            update_dict.update({fees:new_transaction.name})
       

    if list_of_docs:
        for fees in list_of_docs:
            fees_doc = frappe.get_doc("Fees",fees)
            if (fees_doc.name and fees_doc.student_email and fees_doc.student):
                doc= frappe.new_doc("Payment Request")
                doc.update(make_payment_request(dt="Fees",dn=fees_doc.name,party_type= "Student",party= fees_doc.student,recipient_id= fees_doc.student_email))
                if doc.grand_total > 0:
                    doc.save()
                frappe.db.set_value('Bulk Transaction Log Table',{'parent':update_dict[fees],'parentfield': "bulk_transaction_log_table",'fees':fees},'status','Completed')
                name = frappe.get_doc('Bulk Transaction Log',new_transaction.name)
                name.save()
                    # doc.submit()
                
    return True