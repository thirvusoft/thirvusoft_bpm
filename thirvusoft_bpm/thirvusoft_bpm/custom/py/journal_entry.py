import frappe
def update_fees(doc,event):
    for acc in doc.accounts:
        if acc.reference_type == "Fees" and acc.reference_name and acc.debit_in_account_currency > 0 and acc.credit_in_account_currency == 0 and acc.party_type == 'Student' and acc.party:
            fees = frappe.get_doc('Fees',acc.reference_name)
            fees.append('advance_payments',{
                    'account':acc.account,
                    'amount':acc.debit_in_account_currency
                })
            fees.total_advance_payment += acc.debit_in_account_currency
            fees.save()

