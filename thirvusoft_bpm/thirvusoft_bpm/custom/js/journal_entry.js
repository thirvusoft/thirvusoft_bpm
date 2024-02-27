frappe.ui.form.on('Journal Entry', {
	refresh: function(frm,cdt,cdn) {

        cur_frm.set_query('party', 'accounts',function(frm,cdt,cdn) {
            let row = locals[cdt][cdn]
            if(row.party_type == 'Student'){
                return { 'filters': { 'ts_enabled': 1} };
            }
        });
            
            
	},	
});