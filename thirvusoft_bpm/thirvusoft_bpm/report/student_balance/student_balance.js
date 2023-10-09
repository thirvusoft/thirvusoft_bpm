// Copyright (c) 2023, BPM and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Student Balance"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd":1
		},
		{
			"fieldname": "from_fiscal_year",
			"label": __("From Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd":1,
			on_change:function(value){
				if(frappe.query_report.get_filter_value('to_fiscal_year') && frappe.query_report.get_filter_value('from_fiscal_year')){
					frappe.call({
						'method':"thirvusoft_bpm.thirvusoft_bpm.report.student_balance.student_balance.validate_to_date",
						'args':{
							to_fiscal_year:frappe.query_report.get_filter_value('to_fiscal_year'),
							from_fiscal_year:frappe.query_report.get_filter_value('from_fiscal_year'),
						},
						callback:function(){
							frappe.query_report.refresh();
						}
					})
				}
				else if (!frappe.query_report.get_filter_value('from_fiscal_year') && frappe.query_report.get_filter_value('to_fiscal_year')){
					frappe.msgprint("Kindy Fill <b>From Fiscal year</b> before <b>To Fiscal Year</b>")
					frappe.query_report.set_filter_value('to_fiscal_year', '');
				}
			}
		},
		{
			"fieldname": "to_fiscal_year",
			"label": __("To Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd":1,
			on_change:function(value){
				if(frappe.query_report.get_filter_value('to_fiscal_year') && frappe.query_report.get_filter_value('from_fiscal_year')){
					frappe.call({
						'method':"thirvusoft_bpm.thirvusoft_bpm.report.student_balance.student_balance.validate_to_date",
						'args':{
							to_fiscal_year:frappe.query_report.get_filter_value('to_fiscal_year'),
							from_fiscal_year:frappe.query_report.get_filter_value('from_fiscal_year'),
						},
						callback:function(result){
							frappe.query_report.refresh();
							
						}
					})
				}
				else if (!frappe.query_report.get_filter_value('from_fiscal_year') && frappe.query_report.get_filter_value('to_fiscal_year')){
					frappe.msgprint("Kindy Fill <b>From Fiscal year</b> before <b>To Fiscal Year</b>")
					frappe.query_report.set_filter_value('to_fiscal_year', '');
				}
			}
		},
		{
			"fieldname": "account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account"
		},
		{
			"fieldname": "student",
			"label": __("Student"),
			"fieldtype": "Link",
			"options": "Student"
		},
	],
	onload: function (report) {
		report.page.add_inner_button(__("Bulk Payment Request"), function () {
			const selected_docs = [];
			const list_of_docs = [];
			if(frappe.query_report.data){
			frappe.confirm(__("Do you want to Trigger Bulk Payment Request?"),
			function() {
				
				frappe.call({
                    method:"thirvusoft_bpm.thirvusoft_bpm.custom.py.report.trigger_bulk_message",
                    args:{
						'list_of_docs':frappe.query_report.data
					},
					callback:function(frm){
                        // frappe.show_alert({message:__('Payment Request Created Successfully'), indicator:'green'});
                    }
                })
			

			},
			function() {
                console.log("Operation Aborted")
            }
			);
		}			
		else{
			frappe.msgprint("No Data Available")
		}

	})
	}
};
