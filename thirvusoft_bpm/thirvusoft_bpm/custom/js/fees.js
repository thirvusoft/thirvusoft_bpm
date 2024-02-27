frappe.ui.form.on('Fees', {
	refresh: function(frm) {
        frm.set_query('student', function() {
          return { 'filters': { 'ts_enabled': 1} };
        });
    //    if(!frm.doc.__islocal){
    //     frm.add_custom_button(__("Advance Payments"), ()=> {
    //             frappe.call({
    //                 method:"thirvusoft_bpm.thirvusoft_bpm.custom.py.fees.update_advance_payments",
    //                 args:{
    //                     'name':frm.doc.name
    //                 },
    //                 callback:function(res){
    //                     frm.refresh();
    //                 }
    //             })
    //         }, __('Update'));
    //    }
	},
	
});