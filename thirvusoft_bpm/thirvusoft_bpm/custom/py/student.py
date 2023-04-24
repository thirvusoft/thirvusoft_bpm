import frappe
def validate_wapp_enable(doc,event):
    check = 0
    for i in doc.guardians:
        if i.enable_whatsapp_message == 1:
            check = 1
            break
    if check == 0:
        frappe.throw('Kindly enable atleast one guardian for Whatsapp Message')