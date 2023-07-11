// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Admission', {
	edu_branch: function(frm) {
		if(frm.doc.edu_branch){
			frappe.call({
				method: "thirvusoft_bpm.thirvusoft_bpm.doctype.admission.admission.series_no",
				args: {
					edu_branch: frm.doc.edu_branch
				},
				callback:function(res){
					cur_frm.set_value('series_number',res.message)
				}
			});
		}
		
	}
});
