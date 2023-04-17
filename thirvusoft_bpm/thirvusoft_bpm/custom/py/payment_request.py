import frappe
def get_advance_entries(doc,event):
    gl_entry = frappe.get_all('GL Entry',{'debit':['>',0],'is_cancelled':0,'credit':0,'party_type':doc.party_type,'party':doc.party,'against_voucher':doc.reference_name,'voucher_no':['!=',doc.reference_name]},['account','debit'])
    text = ''
    for entry in gl_entry:
        text += f'{entry["account"]} -> {entry["debit"]}' if text !='' else f'<br>{entry["account"]} -> {entry["debit"]}'
    
    doc.advance_payments = text