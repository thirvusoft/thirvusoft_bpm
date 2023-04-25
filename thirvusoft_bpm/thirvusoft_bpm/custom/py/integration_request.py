import frappe
def update_expiry_date(doc,event):
    if(doc.reference_doctype=='Payment Request') and doc.reference_docname:
        pay_doc = frappe.get_doc('Payment Request',doc.reference_docname)
        if(pay_doc.reference_doctype=='Fees') and pay_doc.reference_name:
            fee_doc =  frappe.get_doc('Fees',pay_doc.reference_name)
            doc.expiry_date = fee_doc.due_date