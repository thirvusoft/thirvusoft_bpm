frappe.listview_settings['Fees'] = {
	add_fields: ["grand_total", "outstanding_amount", "due_date"],
	get_indicator: function(doc) {
		if(flt(doc.outstanding_amount)==0) {
			return [__("Paid"), "green", "outstanding_amount,=,0"];
		} else if (flt(doc.outstanding_amount) > 0 && doc.due_date >= frappe.datetime.get_today()) {
			return [__("Unpaid"), "orange", "outstanding_amount,>,0|due_date,>,Today"];
		} else if (flt(doc.outstanding_amount) > 0 && doc.due_date < frappe.datetime.get_today()) {
			return [__("Overdue"), "red", "outstanding_amount,>,0|due_date,<=,Today"];
		}
	},
	onload: function(list_view) {
		list_view.page.add_actions_menu_item(__("Bulk Payment Request"), function() {
			const selected_docs = list_view.get_checked_items();
			const list_of_docs = list_view.get_checked_items(true);
			for (let doc of selected_docs) {
				if (doc.docstatus !== 1) {
					frappe.throw(__("Payment Request can only be generated from a submitted document"));
				}
			}
			frappe.confirm(__("Do you want to Trigger Bulk Payment Request?"),
			function() {
				frappe.call({
                    method:"thirvusoft_bpm.thirvusoft_bpm.custom.py.fees.trigger_bulk_message",
                    args:{
						'list_of_docs':list_of_docs
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
		});
	},

};
