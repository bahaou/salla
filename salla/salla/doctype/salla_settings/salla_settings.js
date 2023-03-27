// Copyright (c) 2023, baha and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salla Settings', {
	// refresh: function(frm) {

	// }
	authorize1 : function(frm){
		console.log("auth");
		frappe.call({
			method:"authorize",
			doc:frm.doc,
			callback(r){
				if (r.message=="200"){
					frm.reload_doc()
				}
			}
		})
	},
	refresh_t : function(frm){
		frappe.call({
			method:"refresh_t",
			doc:frm.doc,
			callback(r){
				if (r.message=="200"){
					frm.reload_doc()
				}
			}
		})
	}
});
