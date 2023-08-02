import frappe
import json
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request

@frappe.whitelist()

def trigger_bulk_message(list_of_docs):
    list_of_docs = json.loads(list_of_docs)
    frappe.enqueue(create_payment_request, list_of_docs = list_of_docs)
    frappe.msgprint("Payment Request Will Be Creating In Backgroud Within 20 Minutes.")

    
def create_payment_request(list_of_docs=None):
    update_dict = {}
    if list_of_docs:
        new_transaction = frappe.new_doc('Bulk Transaction Log')
        for fees in list_of_docs:
            
            new_transaction.append('bulk_transaction_log_table',{
                'fees':fees,
                'status':"Pending"
            })
            new_transaction.save()
            update_dict.update({fees:new_transaction.name})
       

    if list_of_docs:
        for fees in list_of_docs:
            fees_doc = frappe.get_doc("Fees",fees)
            if (fees_doc.name and fees_doc.student_email and fees_doc.student):
                doc= frappe.new_doc("Payment Request")
                doc.update(make_payment_request(dt="Fees",dn=fees_doc.name,party_type= "Student",party= fees_doc.student,recipient_id= fees_doc.student_email))
                doc.mode_of_payment = 'Gateway'
                doc.payment_request_type = 'Inward'
                doc.print_format = frappe.db.get_value(
                    "Property Setter",
                    dict(property="default_print_format", doc_type="Fees"),
                    "value",
                )
                # if doc.grand_total > 0:
                filters = {'student':fees_doc.student,'outstanding_amount':['!=',0],'docstatus':1}
                if fees_doc.name:
                    filters.update({'name':['!=',fees_doc.name]})
                sum = frappe.get_all('Fees',filters,['sum(outstanding_amount) as sum'])
                previous_outstanding_amount = sum[0].get('sum') if sum else 0
                # doc.grand_total += previous_outstanding_amount
                doc.grand_total = fees_doc.net_payable
                # doc.grand_total = fees_doc.outstanding_amount
                doc.save()
                frappe.db.set_value('Bulk Transaction Log Table',{'parent':update_dict[fees],'parentfield': "bulk_transaction_log_table",'fees':fees},'status','Completed')
                name = frappe.get_doc('Bulk Transaction Log',new_transaction.name)
                name.save()
                    # doc.submit()
                
    return True

@frappe.whitelist()
def update_advance_payments(name):
    fees = frappe.get_doc('Fees',name)
    gl_entry = frappe.get_all('GL Entry',{'debit':['>',0],'is_cancelled':0,'credit':0,'party_type':'Student','party':fees.student,'against_voucher':name,'voucher_no':['!=',name]},['account','debit'])
    fees.advance_payments = []
    fees.total_advance_payment = 0
    for entry in gl_entry:
        fees.append('advance_payments',{
            'account':entry['account'],
            'amount':entry['debit']
        })
        fees.total_advance_payment += entry['debit']
    fees.save()
    return True

def previous_outstanding_amount(doc,event):
    filters = {'student':doc.student,'outstanding_amount':['!=',0],'docstatus':1}
    allow_outstanding = True
    if frappe.db.get_value("Company",doc.company,'annual_fees_category'):
        for cat in doc.components:
            if cat.fees_category == frappe.db.get_value("Company",doc.company,'annual_fees_category'):
                allow_outstanding = False
                break
    if doc.name:
        filters.update({'name':['!=',doc.name]})
    if doc.company and frappe.db.get_value("Company",doc.company,'outstanding_receivable_account'):
        filters.update({'receivable_account':['=',frappe.db.get_value("Company",doc.company,'outstanding_receivable_account')]})
    sum = frappe.get_all('Fees',filters,['sum(outstanding_amount) as sum'])
    # if allow_outstanding:
    #     doc.previous_outstanding_amount = sum[0].get('sum') if sum else 0
    # else:
    #     doc.previous_outstanding_amount  = 0
    doc.net_total = doc.grand_total
    if frappe.db.get_value('Company',doc.company,'enable_annual_discounting'):
        if doc.receivable_account == frappe.db.get_value('Company',doc.company,'receivable_account_head_') and  doc.income_account == frappe.db.get_value('Company',doc.company,'income_account_head'):
            doc.grand_total = doc.net_total - (doc.net_total * (frappe.db.get_value('Company',doc.company,'annual_discount'))/100)
        else:
            doc.grand_total  = doc.net_total
    else:
            doc.grand_total  = doc.net_total
    if frappe.db.get_value('Company',doc.company,'enable_prevoius_amount'):
        if not doc.disable_previous_outstanding_amount_ and allow_outstanding:
            doc.net_payable = doc.grand_total + (doc.previous_outstanding_amount or 0)
            # doc.outstanding_amount  = doc.grand_total
        else:
            doc.net_payable = doc.net_total
            doc.outstanding_amount  = doc.grand_total
    else:
        # doc.previous_outstanding_amount  = 0
        doc.net_payable = doc.net_total
        # doc.outstanding_amount  = doc.grand_total