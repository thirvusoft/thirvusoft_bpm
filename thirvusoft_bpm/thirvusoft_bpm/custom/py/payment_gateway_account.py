import frappe
from erpnext.accounts.doctype.payment_gateway_account.payment_gateway_account import PaymentGatewayAccount
class Autoname(PaymentGatewayAccount):
	def autoname(self):
		abbr = frappe.get_value("Company",self.company,'abbr')
		self.name = self.payment_gateway + " - " + abbr
	
	def validate(self):
		self.currency = frappe.db.get_value("Account", self.payment_account, "account_currency")

		# self.update_default_payment_gateway()
		self.set_as_default_if_not_set()