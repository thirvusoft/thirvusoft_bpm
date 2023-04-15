import frappe
from erpnext.accounts.doctype.payment_gateway_account.payment_gateway_account import PaymentGatewayAccount
class Autoname(PaymentGatewayAccount):
    def autoname(self):
        abbr = frappe.get_value("Company",self.company,'abbr')
        self.name = self.payment_gateway + " - " + abbr