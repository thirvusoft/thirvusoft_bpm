# Copyright (c) 2023, BPM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import (
	add_days,
	add_months,
	add_to_date,
	date_diff,
	flt,
	format_date,
	get_datetime,
	nowdate,
)


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
	columns = [
		 {
			"label": _("Posting Date"),
			"fieldtype": "Date",
			"fieldname": "posting_date",
			"width": 100
		},
		{
			"label": _("Student"),
			"fieldtype": "Link",
			"fieldname": "student",
			"options":"Student",
			"width": 110
		},
  		{
			"label": _("Student Name"),
			"fieldtype": "Data",
			"fieldname": "student_name",
			"width": 110
		},
    	{
			"label": _("Fee Structure"),
			"fieldtype": "Link",
			"fieldname": "fee_structure",
   			"options" : "Fee Structure",
			"width": 200
		},
		{
			"label": _("Program"),
			"fieldtype": "Link",
			"fieldname": "program",
			"options":"Program",
			"width": 110
		},
		{
			"label": _("Receivable Account"),
			"fieldtype": "Link",
			"fieldname": "receivable_account",
   			"options":"Account",
			"width": 100
		},
		{
			"label": _("Cost Center"),
			"fieldtype": "Link",
			"fieldname": "cost_center",
   			"options" : "Cost Center",
			"width": 100
		},
  		{
			"label": _("Voucher Type"),
			"fieldtype": "Data",
			"fieldname": "voucher_type",
			"width": 100
		},
    	{
			"label": _("Voucher No"),
			"fieldtype": "Dynamic Link",
			"fieldname": "name",
   			"options" : "voucher_type",
			"width": 100
		},
		 {
			"label": _("Due Date"),
			"fieldtype": "Date",
			"fieldname": "due_date",
			"width": 100
		},
   		{
			"label": _("Invoiced Amount"),
			"fieldtype": "Currency",
			"fieldname": "grand_total",
			"width": 100
		},
    	 {
			"label": _("Paid Amount"),
			"fieldtype": "Currency",
			"fieldname": "paid",
			"width": 100,
			"default":0
		},
       {
			"label": _("Outstanding Amount"),
			"fieldtype": "Currency",
			"fieldname": "outstanding_amount",
			"width": 100,
			"default":0
		},
     	{
			"label": _("Age (Days"),
			"fieldtype": "Int",
			"fieldname": "age",
			"width": 100
		},
      {
			"label": _("0-30"),
			"fieldtype": "Currency",
			"fieldname": "range1",
			"width": 100,
			"default":0
		},
      {
			"label": _("31-60"),
			"fieldtype": "Currency",
			"fieldname": "range2",
			"width": 100,
			"default":0
		},
      {
			"label": _("61-90"),
			"fieldtype": "Currency",
			"fieldname": "range3",
			"width": 100,
			"default":0
		},
      {
			"label": _("91-120"),
			"fieldtype": "Currency",
			"fieldname": "range4",
			"width": 100,
			"default":0
		},
       {
			"label": _("120-Above"),
			"fieldtype": "Currency",
			"fieldname": "range5",
			"width": 100,
			"default":0
		},
		{
			"label": _("Currency"),
			"fieldtype": "Link",
			"fieldname": "currency",
   			"options" : "Currency",
			"width": 100
		},
  		
		
	]
	return columns
def get_data(filters):
	data=[]
	ts_filters={"docstatus": 1}
	if filters.get("company"):
		ts_filters["company"] = filters["company"]
	if filters.get("student"):
		ts_filters["student"] = filters["student"]
	if filters.get("party_account"):
		ts_filters["receivable_account"] = filters["party_account"]
	if filters.get("cost_center"):
		ts_filters["cost_center"] = filters["cost_center"]
	if filters.get("report_date"):
		ts_filters["posting_date"] =['<', filters["report_date"]]
	if filters.get("program"):
		ts_filters["program"] = filters["program"]
	if filters.get("student_group"):
		studentgroup=frappe.db.get_list('Student Group Student', filters={'parent': filters["student_group"]}, pluck="student")
		ts_filters["student"]=['in', studentgroup]
	if filters.get("student") and filters.get("student_group") :
		studentgroup=frappe.db.get_list('Student Group Student', filters={'parent': filters["student_group"]}, pluck="student")
		if filters.get("student") in studentgroup:
			ts_filters["student"] = filters["student"]
		else:
			ts_filters["student"]=['in', []]
		


	posting_date1 = filters["report_date"]
	ageing_based_on = filters.get("ageing_based_on")
	{}
	fee=frappe.db.get_all("Fees", filters=ts_filters, fields=["name","student", "student_name", "posting_date", "due_date", "grand_total", "previous_outstanding_amount", "net_total", "outstanding_amount", "cost_center", "receivable_account", "currency", "program", "fee_structure"], order_by=f"""{"fee_structure, " if (filters.get("group_by_fee_structure")) else ''} student""")
	payment_ent = frappe.db.get_all("Payment Entry", filters={"docstatus":1, "party_type":"Student", "payment_type":"Receive"}, fields=["name", "party", "party_name", "posting_date", "paid_amount", "cost_center"])
	for i in fee:
		i["voucher_type"] ="Fees"
		i["paid"]=(i.grand_total)-(i.outstanding_amount)
		if filters.get("ageing_based_on") == "Posting Date":
			i["age"]= date_diff(posting_date1, i.posting_date)
			if i["age"] <= 30:
				i["range1"] =i["outstanding_amount"]
				i["range2"] =0
				i["range3"] =0
				i["range4"] =0
				i["range5"] =0
			elif i["age"] <= 60:
				i["range2"] =i["outstanding_amount"]
				i["range1"] =0
				i["range3"] =0
				i["range4"] =0
				i["range5"] =0
			elif i["age"] <= 90:
				i["range3"] =i["outstanding_amount"]
				i["range2"] =0
				i["range1"] =0
				i["range4"] =0
				i["range5"] =0
			elif i["age"] <= 120:
				i["range4"] =i["outstanding_amount"]
				i["range2"] =0
				i["range3"] =0
				i["range1"] =0
				i["range5"] =0
			elif i["age"] > 120:
				i["range5"] =i["outstanding_amount"]
				i["range2"] =0
				i["range3"] =0
				i["range4"] =0
				i["range1"] =0
		if filters.get("ageing_based_on") == "Due Date":
			i["age"]=date_diff(posting_date1, i.due_date)
			if i["age"] <= 30:
				i["range1"] =i["outstanding_amount"]
				i["range2"] =0
				i["range3"] =0
				i["range4"] =0
				i["range5"] =0
			elif i["age"] <= 60:
				i["range2"] =i["outstanding_amount"]
				i["range1"] =0
				i["range3"] =0
				i["range4"] =0
				i["range5"] =0
			elif i["age"] <= 90:
				i["range3"] =i["outstanding_amount"]
				i["range2"] =0
				i["range1"] =0
				i["range4"] =0
				i["range5"] =0
			elif i["age"] <= 120:
				i["range4"] =i["outstanding_amount"]
				i["range2"] =0
				i["range3"] =0
				i["range1"] =0
				i["range5"] =0
			elif i["age"] > 120:
				i["range5"] =i["outstanding_amount"]
				i["range2"] =0
				i["range3"] =0
				i["range4"] =0
				i["range1"] =0
	if not filters.get("group_by_party") and not filters.get("group_by_fee_structure"):
		return fee
	total1=0
	total2=0
	total3=0
	total4=0
	total5=0
	total6=0
	total7=0
	total8=0
	final=[]
	for i in range(len(fee)-1):
		total1 +=fee[i]["grand_total"]
		total2 +=fee[i]["paid"]
		total3 +=fee[i]["outstanding_amount"]
		total4 +=fee[i].get("range1") or 0
		total5 +=fee[i].get("range2") or 0
		total6 +=fee[i].get("range3") or 0
		total7 +=fee[i].get("range4") or 0
		total8 +=fee[i].get("range5") or 0
		final.append(fee[i])
		
		if f"""{fee[i]["student"] if filters.get("group_by_party") else ""}{fee[i]["fee_structure"] if filters.get("group_by_fee_structure") else ""}"""!= f"""{fee[i+1]["student"] if filters.get("group_by_party") else ""}{fee[i+1]["fee_structure"] if filters.get("group_by_fee_structure") else ""}""":
			total={}
			total["grand_total"]=total1
			total["paid"]=total2
			total["outstanding_amount"]=total3
			total["range1"]=total4
			total["range2"]=total5
			total["range3"]=total6
			total["range4"]=total7
			total["range5"]=total8
			final.append(total)
			total1=0
			total2=0
			total3=0
			total4=0
			total5=0
			total6=0
			total7=0
			total8=0
	total1 +=fee[i]["grand_total"]
	total2 +=fee[i]["paid"]
	total3 +=fee[i]["outstanding_amount"]
	total4 +=fee[i].get("range1") or 0
	total5 +=fee[i].get("range2") or 0
	total6 +=fee[i].get("range3") or 0
	total7 +=fee[i].get("range4") or 0
	total8 +=fee[i].get("range5") or 0
	final.append(fee[i])
	total={}
	total["grand_total"]=total1
	total["paid"]=total2
	total["outstanding_amount"]=total3
	total["range1"]=total4
	total["range2"]=total5
	total["range3"]=total6
	total["range4"]=total7
	total["range5"]=total8
	final.append(total)
	total1=0
	total2=0
	total3=0
	total4=0
	total5=0
	total6=0
	total7=0
	total8=0
	
	return final
		

def get_chart_data(fee):
	rows = []
	for row in fee:
		row = frappe._dict(row)
		if not cint(row.bold):
			values = [row.range1, row.range2, row.range3, row.range4, row.range5]
			precision = cint(frappe.db.get_default("float_precision")) or 2
			rows.append({"values": [flt(val, precision) for val in values]})

	fee.chart = {
		"data": {"labels": self.ageing_column_labels, "datasets": rows},
		"type": "percentage",
	}