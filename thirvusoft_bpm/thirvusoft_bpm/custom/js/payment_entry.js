frappe.ui.form.on('Payment Entry', {
	paid_from: function(frm) {
        frm.set_df_property("reference_date",'reqd',0)
        frm.set_df_property("reference_no",'reqd',0)
	},
	paid_to:function(frm){
        frm.set_df_property("reference_date",'reqd',0)
        frm.set_df_property("reference_no",'reqd',0)
    },
    party_type:function(frm){
        if (frm.doc.party_type == "Student") {
                cur_frm.fields_dict.party.get_query = function() {
                 return {
                     filters: {
                         "ts_enabled": 1
                     }
                 };
            };
        }
    }
});