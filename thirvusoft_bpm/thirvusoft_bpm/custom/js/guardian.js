frappe.ui.form.on('Guardian', {
	onload: function(frm) {
        if(!frm.doc.__islocal){
            // frappe.call({
            //     method:"thirvusoft_bpm.thirvusoft_bpm.custom.py.guardian.update_student_table",
            //     args:{
            //         'name':frm.doc.name
            //     },
            //     callback:function(res){
            //         console.log('--')
            //         frm.refresh()
            //         // frappe.show_alert({message:__('Payment Request Created Successfully'), indicator:'green'});
            //     }
            // })
        }
	},
	
});