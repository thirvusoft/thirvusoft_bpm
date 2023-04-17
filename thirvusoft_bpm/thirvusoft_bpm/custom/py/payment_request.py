import frappe
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