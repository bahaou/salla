import frappe



def get_indicator(doc):
	module=frappe.db.get_value('DocType',doc,"module")
	app_name=frappe.db.get_value("Module Def",module,"app_name")
	module=module.lower().replace(' ','_')
	app_name=app_name.lower().replace(' ','_')
	doc=doc.lower().replace(' ','_')
	path='{}/{}/{}/doctype/{}/{}_list.js'.format(app_name,app_name,module,doc,doc)
	return(path)
