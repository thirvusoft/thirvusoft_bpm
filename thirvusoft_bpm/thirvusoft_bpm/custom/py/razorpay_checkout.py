import frappe
from frappe.utils import getdate
@frappe.whitelist()
def check_expiry_date(token):
    if getdate(frappe.db.get_value('Integration Request',token,'expiry_date')) >= getdate() :
        print(getdate(frappe.db.get_value('Integration Request',token,'expiry_date')))
        print(getdate())
        return True
    else:
        return False