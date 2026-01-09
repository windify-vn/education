# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See LICENSE

import frappe

def set_cookie_domain():
	"""Set cookie domain for all cookies to enable subdomain sharing"""
	
	# Get cookie domain from configuration
	cookie_domain = frappe.conf.get("cookie_domain")
	if not cookie_domain:
		# Auto-detect domain for windify.edu.vn subdomains
		if hasattr(frappe.local, 'request') and frappe.local.request:
			host = frappe.local.request.host
			if host and ('windify.edu.vn' in host or 'education.windify.edu.vn' in host or 'robo.windify.edu.vn' in host):
				cookie_domain = '.windify.edu.vn'
			else:
				return
		else:
			return
	
	# Override cookie manager to use configured domain
	if hasattr(frappe.local, 'cookie_manager') and frappe.local.cookie_manager:
		original_set_cookie = frappe.local.cookie_manager.set_cookie
		
		def custom_set_cookie(key, value, expires=None, secure=False, httponly=False, 
							samesite="Lax", max_age=None, deduplicate=False, domain=None):
			# Use configured domain if not specified
			if domain is None:
				domain = cookie_domain
			return original_set_cookie(key, value, expires, secure, httponly, 
									samesite, max_age, deduplicate, domain)
		
		frappe.local.cookie_manager.set_cookie = custom_set_cookie
		
		# Also override flush_cookies to include domain
		original_flush_cookies = frappe.local.cookie_manager.flush_cookies
		
		def custom_flush_cookies(response):
			from urllib.parse import quote
			import datetime
			
			for key, opts in frappe.local.cookie_manager.cookies.items():
				response.set_cookie(
					key,
					quote((opts.get("value") or "").encode("utf-8")),
					expires=opts.get("expires"),
					secure=opts.get("secure"),
					httponly=opts.get("httponly"),
					samesite=opts.get("samesite"),
					max_age=opts.get("max_age"),
					domain=opts.get("domain"),
				)

			# expires yesterday!
			expires = datetime.datetime.now() + datetime.timedelta(days=-1)
			for key in set(frappe.local.cookie_manager.to_delete):
				response.set_cookie(key, "", expires=expires)
		
		frappe.local.cookie_manager.flush_cookies = custom_flush_cookies

