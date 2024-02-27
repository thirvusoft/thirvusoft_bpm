import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def payment_entry_customizations():
    make_property_setter('Payment Entry', "reference_no", "allow_on_submit", 1, "Check")
    make_property_setter('Payment Entry', "reference_date", "allow_on_submit", 1, "Check")
    make_property_setter('Payment Entry', "reference_no", "mandatory_depends_on", '', "Small Text")
    make_property_setter('Payment Entry', "reference_date", "mandatory_depends_on", '', "Small Text")
    create_party_type()
    
def create_party_type():
    if not frappe.db.exists('Party Type',{'account_type':"Receivable",'party_type':"Student Applicant"}):
        doc = frappe.new_doc('Party Type')
        doc.account_type = 'Receivable'
        doc.party_type = 'Student Applicant'
        doc.flags.ignore_permissions = True
        doc.save()