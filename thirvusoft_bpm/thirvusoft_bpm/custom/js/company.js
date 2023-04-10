frappe.ui.form.on('Company', {
    refresh: function(frm){
        frm.add_custom_button(__("Bulk Message"), ()=> {
            frappe.confirm(__("Do you want to Trigger Bulk Message?"),
			function() {
				frappe.call({
                    method:"thirvusoft_bpm.thirvusoft_bpm.custom.py.company.trigger_bulk_message",
                    args:{
                        company:frm.doc.name
                    },
                    callback:function(frm){
                        frappe.show_alert({message:__('Payment Request Created Successfully'), indicator:'green'});
                    }
                })
			},
			function() {
                console.log("Operation Aborted")
            }
		);
        });
    }
})