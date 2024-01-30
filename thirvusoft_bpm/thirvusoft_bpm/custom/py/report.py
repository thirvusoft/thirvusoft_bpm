import frappe
import json
from erpnext.accounts.doctype.payment_request.payment_request import get_gateway_details,get_amount
from erpnext.accounts.party import get_party_account, get_party_bank_account
from frappe import _
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file
from frappe.email.doctype.auto_email_report.auto_email_report import update_field_types,make_links
from frappe.utils import (
	get_url_to_report,
	global_date_format,
	now,
	format_time
)

@frappe.whitelist()
def trigger_bulk_message(list_of_docs,students,filters):
	filters = json.loads(filters)
	result = []
	frappe.enqueue(create_list, list_of_docs = list_of_docs,result = result,filters=filters,students=students,queue="long")

def create_list(list_of_docs,result,filters,students):
	list_of_docs = json.loads(list_of_docs)
	students = json.loads(students)
	idx = 0
	list_of_docs = [d for d in list_of_docs if d.get("party")]
	for i in list_of_docs:
		if i.get('party') == "<b>Result</b>" and (list_of_docs[idx-1].get('party') in students or filters[0].get('type') != 'Selected Students') and i.get('net') > 0 :
				row = i
				row.update({'student':list_of_docs[idx-1].get('party')})
				result.append(i)
		idx += 1
	create_payment_request(list_of_docs = result,filters=filters)

def create_payment_request(list_of_docs=None,filters=None):
	update_dict = {}
	if list_of_docs:
		new_transaction = frappe.new_doc('Bulk Transaction Log')
		idx  = 0
		for fees in list_of_docs:
			fees_doc = frappe.get_list("Fees",{'student':fees.get('student'),'docstatus':1,'outstanding_amount':['>',0]},order_by='creation')
			if fees_doc:
				fees_doc = fees_doc[0]
				fees.update({'name': fees_doc.get('name')})
				new_transaction.append('bulk_transaction_log_table',{
					'student':fees.get('student'),
					'status':"Pending",
					'fees':fees_doc.get('name'),
					'outstanding_amount':fees.get('net')
				})
				idx += 1
				if not new_transaction.name:
					new_transaction.save()
				update_dict.update({fees_doc.get('name'):new_transaction.name})

		new_transaction.save()
		
		# get_report_content(filters,new_transaction)	

	if list_of_docs:
		for fees in list_of_docs:
			student = frappe.get_doc("Student",fees.get('student'))
			if fees.get('name'):
				fee_doc = frappe.get_doc("Fees",fees.get('name'))
			else:
				fee_doc = None
			if (student and fee_doc and fee_doc.student_email and fees.get('student')):
				doc= frappe.new_doc("Payment Request")
				doc.update(make_payment_request(dt="Fees",dn=fees.get('name'),party_type= "Student",party= fees.get('student'),recipient_id= fee_doc.student_email))
				doc.mode_of_payment = 'Gateway'
				doc.payment_request_type = 'Inward'
				doc.print_format = frappe.db.get_value(
					"Property Setter",
					dict(property="default_print_format", doc_type="Fees"),
					"value",
				)
				doc.bulk_transaction = 1
				doc.grand_total =  fees.get('net')
				doc.student_balance = fees.get('net')
				doc.save()

				frappe.db.set_value('Bulk Transaction Log Table',{'parent':update_dict[fees.get('name')],'parentfield': "bulk_transaction_log_table",'fees':fees.get('name')},'status','Completed')
				name = frappe.get_doc('Bulk Transaction Log',new_transaction.name)
				name.db_update()

	return True


def get_report_content(filters,new_transaction):
	"""Returns file in for the report in given format"""
	report = frappe.get_doc("Report", 'Student Balance')


	columns, data = report.get_data(
		user="Administrator",
		filters=filters[0],
		as_dict=True,
		ignore_prepared_report=True,
		are_default_filters=False,
	)

	# add serial numbers
	columns.insert(0, frappe._dict(fieldname="idx", label="", width="30px"))
	for i in range(len(data)):
		data[i]["idx"] = i + 1

	columns, data = make_links(columns, data)
	columns = update_field_types(columns)

	save_file(new_transaction.name, get_pdf(get_html_table(columns,data),{"orientation": 'Landscape'}), new_transaction.doctype, new_transaction.name)           

def get_html_table(columns=None, data=None):
    
	date_time = global_date_format(now()) + " " + format_time(now())
	report_doctype = frappe.db.get_value("Report", "Student Balance", "ref_doctype")

	return frappe.render_template(
		"thirvusoft_bpm/custom/py/auto_email_report.html",
		{
			"title": "Student Balance",
			"description": '',
			"date_time": date_time,
			"columns": columns,
			"data": data,
			"report_url": get_url_to_report("Student Balance", 'Script Report', report_doctype),
			"report_name": "Student Balance",
		},
	)