import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def payment_entry_customizations():
    make_property_setter('Payment Entry', "reference_no", "allow_on_submit", 1, "Check")
    make_property_setter('Payment Entry', "reference_date", "allow_on_submit", 1, "Check")
    make_property_setter('Payment Entry', "reference_no", "mandatory_depends_on", '', "Small Text")
    make_property_setter('Payment Entry', "reference_date", "mandatory_depends_on", '', "Small Text")

