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
		{
			"fieldname": "program",
			"label": __("Program"),
			"fieldtype": "Link",
			"options": "Program"
		},
		{
			"fieldname": "threshold_amount",
			"label": __("Threshold Amount"),
			"fieldtype": "Currency"
		},
		{
			"fieldname": "type",
			"label": __("Select Type"),
			"options": "All Students\nSelected Students",
			"fieldtype": "Select",
			'default':'All Students'

		},
	],
	onload: function (report) {
		report.page.add_inner_button(__("Bulk Payment Request"), async function () {

			if(frappe.query_report.data){
			let filters  = [];
			const dic = { };
			await frappe.query_report.filters.forEach(element => {
				
				dic[element.fieldname] = element.value
				
			});
			filters.push(dic)

			frappe.confirm(__("Do you want to Trigger Bulk Payment Request?"),
			async function() {
				await frappe.msgprint("Payment Request Will Be Creating In Backgroud Within 30 Minutes.")

				frappe.call({
                    method:"thirvusoft_bpm.thirvusoft_bpm.custom.py.report.trigger_bulk_message",
                    args:{
						'list_of_docs':frappe.query_report.data,
						'students':frappe.query_report.students,
						'filters':filters
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
	},
};

function get_check(event, party) {
    if (event.target.checked == true) {
        if (!frappe.query_report.students) {
            frappe.query_report.students = [party];
        } else {
            frappe.query_report.students.push(party);
        }
    } else {
        if (frappe.query_report.students) {
            frappe.query_report.students = frappe.query_report.students.filter(item => item !== party);
        }
    }
}

frappe.realtime.on("empty_students", function(data) {
	frappe.query_report.students=[]

});