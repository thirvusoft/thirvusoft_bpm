import frappe
from frappe.utils import getdate
@frappe.whitelist(allow_guest= True)
def check_expiry_date(token):
    if getdate(frappe.db.get_value('Integration Request',token,'expiry_date')) >= getdate() :
        return True
    else:
        message = ''
        if frappe.db.get_value('Integration Request',token,'reference_doctype') == 'Payment Request' and frappe.db.get_value('Integration Request',token,'reference_docname'):
            if frappe.db.get_value('Payment Request',frappe.db.get_value('Integration Request',token,'reference_docname'),'payment_gateway_account'):
                doc_name = frappe.db.get_value('Payment Request',frappe.db.get_value('Integration Request',token,'reference_docname'),'payment_gateway_account')
                doc = frappe.get_doc('Payment Gateway Account',doc_name)
                message = doc.default_message_for_expiry_date_remainder
        return message,False