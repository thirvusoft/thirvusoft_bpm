# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Admission(Document):
	pass
	# def autoname(self):
	# 	self.name = self.edu_branch +' - '+ self.series_no
	# 	self.admission = self.edu_branch +' - '+ self.series_no

@frappe.whitelist()
def series_no(edu_branch):
	no_list = frappe.get_list("Admission",['series_no'],{'edu_branch':edu_branch},order_by='series_no')
	if no_list:
		series = no_list[-1].get('series_no') or 0
		try:
			return float(series) + 1
		except:
			return 1
	else:
		return 1