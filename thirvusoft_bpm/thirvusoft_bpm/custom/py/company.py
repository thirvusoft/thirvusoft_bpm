import frappe
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request

@frappe.whitelist()

def trigger_bulk_message(company):
    frappe.enqueue(create_payment_request, company = company)
    frappe.msgprint("Payment Request Will Be Creating In Backgroud Within 15 Minutes.")

    
def create_payment_request(company=None):
    if company:
        student_fees = frappe.get_all('Fees',{'company':company},['name','student','student_email'])
        for fees in student_fees:
            if (fees['name'] and fees['student_email'] and fees['student']):
                doc= frappe.new_doc("Payment Request")
                doc.update(make_payment_request(dt="Fees",dn=fees['name'],party_type= "Student",party= fees['student'],recipient_id= fees['student_email']))
                if doc['grand_total'] > 0:
                    doc.save()
                    doc.submit()
    return True