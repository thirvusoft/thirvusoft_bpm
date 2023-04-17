# Copyright (c) 2023, BPM and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class BulkTransactionLog(Document):
	def validate(self):
		status = 'Completed'
		for i in self.bulk_transaction_log_table:
			if i.status != "Completed":
				status = 'Pending'
				break
		self.transaction_status = status
