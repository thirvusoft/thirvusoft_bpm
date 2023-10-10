import frappe
import json
from erpnext.accounts.doctype.payment_request.payment_request import get_gateway_details,get_amount
from erpnext.accounts.party import get_party_account, get_party_bank_account
from frappe import _
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request

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

	# create_payment_request(result)
	frappe.enqueue(create_payment_request, list_of_docs = result)
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
				fees_doc = frappe.get_list("Fees",{'student':fees.get('student'),'outstanding_amount':['>',0]},order_by='creation')
				if fees_doc:
					fees_doc = fees_doc[0]
				else:
					fees_doc = None
				doc.update(make_payment_request(dt="Fees",dn=fees_doc.name,party_type= "Student",party= fees.get('student'),recipient_id= student.student_email_id))
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

# @frappe.whitelist(allow_guest=True)
# def make_payment_request(**args):
# 	"""Make payment request"""

# 	args = frappe._dict(args)

# 	ref_doc = frappe.get_doc(args.dt, args.dn)
# 	gateway_account = get_gateway_details(args) or frappe._dict()

# 	grand_total = get_amount(ref_doc, gateway_account.get("payment_account"))
# 	if args.loyalty_points and args.dt == "Sales Order":
# 		from erpnext.accounts.doctype.loyalty_program.loyalty_program import validate_loyalty_points

# 		loyalty_amount = validate_loyalty_points(ref_doc, int(args.loyalty_points))
# 		frappe.db.set_value(
# 			"Sales Order", args.dn, "loyalty_points", int(args.loyalty_points), update_modified=False
# 		)
# 		frappe.db.set_value(
# 			"Sales Order", args.dn, "loyalty_amount", loyalty_amount, update_modified=False
# 		)
# 		grand_total = grand_total - loyalty_amount

# 	bank_account = (
# 		get_party_bank_account(args.get("party_type"), args.get("party"))
# 		if args.get("party_type")
# 		else ""
# 	)

# 	existing_payment_request = None
# 	if args.order_type == "Shopping Cart":
# 		existing_payment_request = frappe.db.get_value(
# 			"Payment Request",
# 			{"reference_doctype": args.dt, "reference_name": args.dn, "docstatus": ("!=", 2)},
# 		)

# 	if existing_payment_request:
# 		frappe.db.set_value(
# 			"Payment Request", existing_payment_request, "grand_total", grand_total, update_modified=False
# 		)
# 		pr = frappe.get_doc("Payment Request", existing_payment_request)
# 	else:
# 		if args.order_type != "Shopping Cart":
# 			existing_payment_request_amount = get_existing_payment_request_amount(args.dt, args.dn)

# 			if existing_payment_request_amount:
# 				grand_total -= existing_payment_request_amount

# 		pr = frappe.new_doc("Payment Request")
# 		pr.update(
# 			{
# 				"payment_gateway_account": gateway_account.get("name"),
# 				"payment_gateway": gateway_account.get("payment_gateway"),
# 				"payment_account": gateway_account.get("payment_account"),
# 				"payment_channel": gateway_account.get("payment_channel"),
# 				"payment_request_type": args.get("payment_request_type"),
# 				"currency": ref_doc.currency,
# 				"grand_total": grand_total,
# 				"mode_of_payment": args.mode_of_payment,
# 				"email_to": args.recipient_id or ref_doc.owner,
# 				"subject": _("Payment Request for {0}").format(args.dn),
# 				"message": gateway_account.get("message") or get_dummy_message(ref_doc),
# 				"reference_doctype": args.dt,
# 				"reference_name": args.dn,
# 				"party_type": args.get("party_type") or "Customer",
# 				"party": args.get("party") or ref_doc.get("customer"),
# 				"bank_account": bank_account,
# 			}
# 		)
# 		# customization by thirvusoft
# 		if args.dt== "Fees":
# 			net_payable=frappe.get_value("Fees",args.dn,"net_payable")
# 			pr.update(
# 			{
# 				"grand_total": net_payable,
# 			}
# 		)

# 		if args.order_type == "Shopping Cart" or args.mute_email:
# 			pr.flags.mute_email = True

# 		if args.submit_doc:
# 			pr.insert(ignore_permissions=True)
# 			pr.submit()

# 	if args.order_type == "Shopping Cart":
# 		frappe.db.commit()
# 		frappe.local.response["type"] = "redirect"
# 		frappe.local.response["location"] = pr.get_payment_url()

# 	if args.return_doc:
# 		return pr

# 	return pr.as_dict()