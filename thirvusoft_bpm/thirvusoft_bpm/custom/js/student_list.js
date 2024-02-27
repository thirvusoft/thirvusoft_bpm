frappe.listview_settings['Student'] = {
	add_fields: [ "image"],
    get_indicator: function(doc) {
        console.log('ii')
		if(doc.ts_enabled == 0) {
			return [__("Disabled"), "grey", "ts_enabled,=,0"];
		}
        else if(doc.ts_enabled == 1) {
			return [__("Enabled"), "blue", "ts_enabled,=,1"];
		} 
	},
}
