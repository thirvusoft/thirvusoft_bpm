frappe.ui.form.on('Company', {
	refresh: function(frm) {
        frm.set_query('outstanding_receivable_account', function() {
			return { 'filters': { 'company': frm.doc.name } };
		});
	},
	
});