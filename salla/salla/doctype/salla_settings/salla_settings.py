# Copyright (c) 2023, baha and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import requests

from frappe.model.document import Document

class SallaSettings(Document):
	
	@frappe.whitelist()
	def authorize(self):
		id=self.client_id
		secret=self.client_secret
		code=self.authorization_code
		grant_type="authorization_code"
		scope="offline_access"
		redirect_uri='https://modoncompany.modon.deom.com.sa/salla'
		url = "https://accounts.salla.sa/oauth2/token"
		headers = {"Content-Type": "application/x-www-form-urlencoded"}
		payload = {
		    "client_id": id,
		    "client_secret": secret,
		    "grant_type": grant_type,
		    "code": code,
		    "scope": scope,
		    "redirect_uri": redirect_uri
		}
		print(payload)
		response = requests.request("POST", url, data=payload, headers=headers)
		if response.status_code==200:
			r=response.json()
			self.access_token=r['access_token']
			self.refresh_token=r['refresh_token']
			self.save()
			alert("Token regenerated successfully")
		else:
			alert("Error while generating token","red")
		#print(response.__dict__)
		return(response.status_code)
	@frappe.whitelist()
	def refresh_t(self):
		id=self.client_id
		secret=self.client_secret
		code=self.authorization_code
		grant_type="refresh_token"
		refresh_token=self.refresh_token
		url = "https://accounts.salla.sa/oauth2/token"
		redirect_uri='https://modoncompany.modon.deom.com.sa/salla'
		headers = {"Content-Type": "application/json"}
		payload = {
                    "client_id": id,
                    "client_secret": secret,
                    "grant_type": grant_type,
                    "refresh_token":refresh_token,
                    "redirect_uri": redirect_uri
                }
		print(payload)
		response = requests.request("POST", url, data=payload)
		print(response.__dict__)
		if response.status_code==200:
			r=response.json()
			self.refresh_token=r['refresh_token']
			self.access_token=r['access_token']
			self.save()
			alert("Token regenerated successfully")
		else:
			alert("Error while regenerating token","red")
		return(response.status_code)



def alert(msg,color="green"): 
	frappe.msgprint( _(msg), alert=True, indicator=color)
