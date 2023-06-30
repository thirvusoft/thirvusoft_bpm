# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Admission(Document):
    def autoname(self):
        if not self.pre_admission:
            self.name = self.edu_branch +' - '+ self.series_no
            self.admission = self.edu_branch +' - '+ self.series_no
        else:
            self.name = self.edu_branch +' - '+ self.series
            self.admission = self.edu_branch +' - '+ self.series

@frappe.whitelist()
def series_no(edu_branch):
    no_list = frappe.get_list("Admission",['series_no'],{'edu_branch':edu_branch,"pre_admission":0},order_by='series_no')
    if no_list:
        series = no_list[-1].get('series_no') or 0
        try:
            return float(series) + 1
        except:
            return 1
    else:
        return 1