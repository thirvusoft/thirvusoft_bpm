import frappe
import json
from erpnext.accounts.doctype.payment_request.payment_request import get_gateway_details,get_amount
from erpnext.accounts.party import get_party_account, get_party_bank_account
from frappe import _

@frappe.whitelist()

def trigger_bulk_message(list_of_docs):
	list_of_docs = json.loads(list_of_docs)
	result = []
	idx = 0
	list_of_docs = [d for d in list_of_docs if d.get("party")]
	for i in list_of_docs:
		if i.get('party') == "<b>Result</b>" and i.get('net') > 0:
				row = i
				# if not result:
				# 	result.append({'student':frappe.get_value("Student",{'title':list_of_docs[idx-1].get('party_name')},'name')})
				row.update({'student':list_of_docs[idx-1].get('party')})
				result.append(i)
		idx += 1

	create_payment_request(result)
	# frappe.enqueue(create_payment_request, list_of_docs = list_of_docs)
	frappe.msgprint("Payment Request Will Be Creating In Backgroud Within 20 Minutes.")

	
def create_payment_request(list_of_docs=None):
	update_dict = {}
	if list_of_docs:
		new_transaction = frappe.new_doc('Bulk Transaction Log')
		idx  = 0
		for fees in list_of_docs:
			new_transaction.append('bulk_transaction_log_table',{
				'student':fees.get('student'),
				'status':"Pending"
			})
			
			new_transaction.save()
			idx += 1
			# update_dict.update({fees:new_transaction.name})
	

	if list_of_docs:
		for fees in list_of_docs:
			student = frappe.get_doc("Student",fees.get('student'))
			if (student and student.student_email_id and fees.get('student')):
				doc= frappe.new_doc("Payment Request")
				doc.update(make_payment_request(party_type= "Student",party= fees.get('student'),recipient_id= student.student_email_id))
				doc.mode_of_payment = 'Gateway'
				doc.payment_request_type = 'Inward'
				doc.print_format = frappe.db.get_value(
					"Property Setter",
					dict(property="default_print_format", doc_type="Fees"),
					"value",
				)
				
				
				# doc.grand_total += previous_outstanding_amount
				doc.grand_total =  fees.get('net')
				# doc.grand_total = fees_doc.outstanding_amount
				doc.save()
				# frappe.db.set_value('Bulk Transaction Log Table',{'parent':update_dict[fees],'parentfield': "bulk_transaction_log_table",'fees':fees},'status','Completed')
				# name = frappe.get_doc('Bulk Transaction Log',new_transaction.name)
				# name.save()
					# doc.submit()
				
	return True

@frappe.whitelist(allow_guest=True)
def make_payment_request(**args):
	"""Make payment request"""

	args = frappe._dict(args)


	gateway_account = get_gateway_details(args) or frappe._dict()

	
	bank_account = (
		get_party_bank_account(args.get("party_type"), args.get("party"))
		if args.get("party_type")
		else ""
	)

	draft_payment_request = frappe.db.get_value(
		"Payment Request",
		{"reference_doctype": args.dt, "reference_name": args.dn, "docstatus": 0},
	)


	if draft_payment_request:
		frappe.db.set_value(
			"Payment Request", draft_payment_request, "grand_total", grand_total, update_modified=False
		)
		pr = frappe.get_doc("Payment Request", draft_payment_request)
	else:
		pr = frappe.new_doc("Payment Request")
		pr.update(
			{
				"payment_gateway_account": gateway_account.get("name"),
				"payment_gateway": gateway_account.get("payment_gateway"),
				"payment_account": gateway_account.get("payment_account"),
				"payment_channel": gateway_account.get("payment_channel"),
				"payment_request_type": args.get("payment_request_type"),
				"mode_of_payment": args.mode_of_payment,
				"email_to": args.recipient_id ,
				"subject": _("Payment Request for {0}").format(args.dn),
				"message": gateway_account.get("message"),
				"party_type": args.get("party_type") or "Customer",
				"party": args.get("party"),
				"bank_account": bank_account,
			}
		)
		# customization by thirvusoft
		if args.dt== "Fees":
			pr.update(
			{
				"grand_total": net_payable,
			}
		)




		if args.order_type == "Shopping Cart" or args.mute_email:
			pr.flags.mute_email = True

		if args.submit_doc:
			pr.insert(ignore_permissions=True)
			pr.submit()

	if args.order_type == "Shopping Cart":
		frappe.db.commit()
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = pr.get_payment_url()

	if args.return_doc:
		return pr

	return pr.as_dict()