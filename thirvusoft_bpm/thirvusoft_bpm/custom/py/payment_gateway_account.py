import frappe
from erpnext.accounts.doctype.payment_gateway_account.payment_gateway_account import PaymentGatewayAccount
class Autoname(PaymentGatewayAccount):
    def autoname(self):
        company = frappe.get_value('Account',self.payment_account,'company')
        abbr = frappe.get_value("Company",company,'abbr')
        self.name = self.payment_gateway + " - " + abbr