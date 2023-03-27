import frappe
import requests
from frappe.utils import getdate
import itertools
from erpnext.controllers.item_variant import create_variant

def get_items():
	s=frappe.get_doc("Salla Settings")
	price_list=s.price_list
	token = s.access_token or None
	if not token:
		return
	token="Bearer "+token
	url="https://api.salla.dev/admin/v2/products"
	headers = {"Content-Type": "application/json","Authorization": token}
	response = requests.request("GET", url, headers=headers)
	if response.status_code!=200:
		return
	r=response.json()['data']
	item_ids=frappe.db.get_all('Item',fields=["salla_id"])
	categories=frappe.db.get_all('Item Group')
	categories=[c['name'] for c in categories]
	item_ids=[str(i['salla_id']) for i in item_ids]
	old_attributes=frappe.db.get_all('Item Attribute')
	old_attributes=[i['name'].lower() for i in old_attributes]
	old_values=frappe.db.get_all('Item Attribute Value')
	old_values=[i['name'].lower() for i in old_values]
	for i in r:
		if str(i['id']) in item_ids:
			continue
		item_group="Products"
		
		for j in i['categories']:
			item_group=j['name']
			if j['name'] not in categories:
				insert_category(j['name'],j['id'])
				categories.append(j['name'])
		item=frappe.new_doc('Item')
		ues={}
		values={}
		op={}
		val={}
		variant=False
		if len(i['options'])>0:
			item.has_variants=1
			attributes=[]
			for v in i['options']:
				vv=[]
				op[v['id']]=v['name']
				for g in v['values']:
					val[g['id']]=g['name']
					vv.append(g['name'])
					ues[g['name']]=v['name']
				values[v['name']]=vv
				attributes.append(v['name'])
				attributes=list(set(attributes))
			for a in attributes:
				#if a not in old_attributes:
					#insert_attribute(a)
					#old_attributes.append(a)
				attribute=item.append('attributes',{"attribute":a})
			url = "https://api.salla.dev/admin/v2/products/{}/variants".format(i['id'])
			response = requests.request("GET", url, headers=headers)
			variant=True
			variants=response.json()['data']
		item.item_code=str(i['id'])
		item.salla_id=str(i['id'])
		item.item_name=i['name']
		item.item_group=item_group
		if i['main_image']:
			item.image=i['main_image']
		item.insert()
		for v in values:
			if v not in old_attributes:
				insert_attribute(a)
				old_attributes.append(a)
			for k in values[v]:
				if k not in old_values:
					insert_value(v,k)
					old_values.append(k)
		if variant:
			related_options=[]
			values=[]
			for v in variants:
				related_options=[]
				related_option_values=[]
				for r in v['related_option_values']:
					related_option_values.append(val[r])
				args={}
				for o in range(len(related_option_values)):
					args[ues[related_option_values[o]]]=related_option_values[o]
				id=v['id']
				price=v['price']['amount']
				print(price)
				print(args)
				new_variant=create_variant(item=item.name,args=args)
				new_variant.item_code=str(id)
				new_variant.insert()
				item_price=frappe.new_doc('Item Price')
				item_price.price_list=price_list
				item_price.item_code=id
				item_price.price_list_rate=float(price)
				item_price.insert()
	frappe.db.commit()
def get_orders():
	s=frappe.get_doc("Salla Settings")
	if not s.company or not s.customer_group or not s.customer_territory:
		return
	token = s.access_token or None
	if not token:
		return
	token="Bearer "+token
	url="https://api.salla.dev/admin/v2/orders"
	headers = {"Content-Type": "application/json","Authorization": token}
	response = requests.request("GET", url, headers=headers)
	if response.status_code!=200:
		return
	r=response.json()['data']
	customer_ids=frappe.db.get_all('Customer',fields=["salla_id"])
	ids=frappe.db.get_all('Quotation',fields=['id'])
	ids=[str(i["id"]) for i in ids]
	customer_ids=[str(c['salla_id']) for c in customer_ids]
	customer_group=s.customer_group
	territory=s.customer_territory
	for i in r:
		order_id=i['id']
		if str(order_id) in ids:
			continue
		url="https://api.salla.dev/admin/v2/orders/"+str(order_id)
		response = requests.request("GET", url, headers=headers)
		if response.status_code!=200:
			continue
		i=response.json()['data']
		
		customer=i['customer']
		if str(customer['id']) not in customer_ids:
			doc=frappe.new_doc('Customer')
			doc.salla_id=customer['id']
			doc.customer_name=customer['first_name']+" "+customer['last_name']
			doc.customer_group=customer_group
			doc.territory=territory
			doc.type='Individual'
			doc.insert()
			customer_ids.append(str(customer['id']))
			contact=frappe.new_doc('Contact')
			contact.first_name=customer['first_name']
			contact.last_name=customer['last_name']
			contact.status="Open"
			link=contact.append('links',{})
			link.link_doctype='Customer'
			link.link_name=doc.name
			contact.is_primary_contact=1
			phone=contact.append('phone_nos',{})
			phone.phone=str(customer['mobile'])
			phone.is_primary_mobile_no=1
			if customer['email']:
				email=contact.append('email_ids',{})
				email.email_id=customer['email']
				email.is_primary=1
			contact.insert()
			doc.customer_primary_contact=contact.name
			doc.save()
			customer_name=doc.name
		customers=frappe.db.get_all('Customer',filters={'salla_id':str(customer['id'])})
		if len(customers)==0:
			continue
		customer_name=customers[0]['name']
		quot=frappe.new_doc("Quotation",{})
		quot.quotation_to="Customer"
		quot.party_name=customer_name
		quot.order_type="Salla"
		quot.id=i['id']
		d=i['date']['date'][:10]
		quot.transaction_date=d
		d=getdate(d)
		print(d)
		items=i['items']
		tax=0
		for item in items:	
			names=[]
			options= item['options']
			id=item['product']['id']
			for o in options:
				names.append(o['value']['name'])
			variant=''
			variant_id=''
			if len(names)>0:
				variants=frappe.db.get_all('Item',filters={'variant_of':id},fields=['name','item_name'])
				old_names={}
				for v in variants:
					old_names[v['item_name']]=v['name']
				for o in old_names:
					yes=True
					for n in names:
						if n not in o:
							yes=False
							continue
						if yes:
							variant=old_names[o]
			
			new_item=quot.append('items',{})
			new_item.item_code=variant
			new_item.qty=item['quantity']
			amounts=item['amounts']
			tax=amounts['tax']['percent']
			rate=amounts["price_without_tax"]['amount']-amounts['total_discount']['amount']
			new_item.rate=rate
			#new_item.tax_rate=tax
			#new_item.tax_amount=amounts['tax']['amount']['amount']
		taxes=frappe.db.get_all('Sales Taxes and Charges',filters={'rate':tax},fields=['parent'])
		if len(taxes)>0:
			quot.taxes_and_charges=taxes[0]['parent']
		try:
			quot.insert()
		except:
			continue
	frappe.db.commit()


def insert_category(name,id=None):
	doc=frappe.new_doc('Item Group')
	doc.item_group_name=name
	if id:
		doc.salla_id=id
	doc.insert()

def insert_attribute(a):
	print("inserting attribute",a)
	att=frappe.new_doc('Item Attribute')
	att.attribute_name=a
	att.insert()
def insert_value(att,value):
	v=frappe.new_doc('Item Attribute Value')
	v.parent=att
	v.attribute_value=value
	v.abbr=value
	v.parenttype="Item Attribute"
	v.parentfield="item_attribute_values"
	v.insert()
