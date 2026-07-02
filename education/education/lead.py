# Copyright (c) 2026, Windify Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils import nowdate, today


def before_validate(doc, method=None):
	sync_student_name(doc)
	fill_mandatory_defaults(doc)
	sync_employee_owner(doc)
	sync_campaign(doc)
	sync_parent_contact_to_lead(doc)


def fill_mandatory_defaults(doc):
	"""Auto-fill mandatory Lead fields so users don't have to enter them manually."""
	# Lead: First Name
	if not doc.get("first_name"):
		doc.first_name = (
			doc.get("education_student_full_name")
			or doc.get("lead_name")
			or doc.get("email_id")
			or doc.get("mobile_no")
			or "-"
		)

	if doc.get("company_name") == "-":
		doc.company_name = None

	# Lead items reuse Sales Order Item; fill fetched fields in case fetch_from hasn't triggered.
	for item in doc.get("education_items") or []:
		if item.get("item_code") and not item.get("item_name"):
			item_doc = frappe.get_cached_doc("Item", item.item_code)
			item.item_name = item_doc.item_name
			if not item.get("uom"):
				item.uom = item_doc.stock_uom
			if not item.get("description"):
				item.description = item_doc.description

		# Tự động lấy giá niêm yết (price_list_rate) nếu chưa có
		if not item.get("price_list_rate"):
			price = frappe.db.get_value(
				"Item Price", 
				{"item_code": item.item_code, "price_list": "Standard Selling"}, 
				"price_list_rate"
			)
			item.price_list_rate = price or 0

		# Tính rate (giá sau giảm) từ discount_percentage
		discount = flt(item.get("discount_percentage") or 0)
		price_list_rate = flt(item.get("price_list_rate") or 0)
		
		# Nếu user nhập thủ công rate thì ưu tiên, nếu không thì tính từ discount
		# (Frappe client script không chạy trên Lead nên phải tự tính)
		if discount > 0:
			item.rate = price_list_rate * (1 - discount / 100.0)
		elif not item.get("rate"):
			item.rate = price_list_rate

		# Auto-calculate amount
		qty = flt(item.get("qty") or 1)
		rate = flt(item.get("rate") or 0)
		conversion_factor = flt(item.get("conversion_factor") or 1)
		amount = qty * rate
		
		item.conversion_factor = conversion_factor
		item.stock_qty = qty * conversion_factor
		item.amount = amount
		item.base_rate = item.get("base_rate") or rate
		item.base_amount = item.get("base_amount") or amount


def validate(doc, method=None):
	pass


def after_insert(doc, method=None):
	queue_auto_sales_order(doc)


def on_update(doc, method=None):
	queue_auto_sales_order(doc)


def sync_student_name(doc):
	full_name = doc.get("education_student_full_name")
	if not full_name:
		return

	from erpnext.selling.doctype.customer.customer import parse_full_name

	doc.lead_name = full_name
	first_name, middle_name, last_name = parse_full_name(full_name)

	if first_name:
		doc.first_name = first_name
	doc.middle_name = middle_name
	doc.last_name = last_name


def get_lead_display_name(lead):
	return (
		lead.get("education_student_full_name")
		or lead.get("lead_name")
		or None
	)


def sync_employee_owner(doc):
	employee = doc.get("education_lead_owner_employee")
	if not employee:
		return

	user = frappe.db.get_value("Employee", employee, "user_id")
	if user:
		doc.lead_owner = user


def sync_campaign(doc):
	campaign = doc.get("education_campaign")
	if campaign:
		doc.utm_campaign = campaign


def sync_parent_contact_to_lead(doc):
	parent_phone = doc.get("education_parent_phone_number")
	parent_email = doc.get("education_parent_email")

	if parent_phone and not doc.mobile_no:
		doc.mobile_no = parent_phone

	if parent_email and not doc.email_id:
		duplicate_lead = frappe.db.exists(
			"Lead",
			{
				"email_id": parent_email,
				"name": ["!=", doc.name or ""],
			},
		)
		if not duplicate_lead:
			doc.email_id = parent_email


def queue_auto_sales_order(doc):
	if not doc.get("education_auto_create_sales_order"):
		set_auto_order_status(doc, "Skipped")
		return

	if doc.get("education_auto_sales_order"):
		return

	if doc.get("education_auto_order_status") in ("Queued", "Completed"):
		return

	if not doc.get("education_items"):
		set_auto_order_status(doc, "Pending")
		return

	set_auto_order_status(doc, "Queued")
	frappe.enqueue(
		"education.education.lead.create_sales_order_for_lead",
		queue="short",
		enqueue_after_commit=True,
		lead_name=doc.name,
	)


def create_sales_order_for_lead(lead_name):
	lead = frappe.get_doc("Lead", lead_name)

	if lead.get("education_auto_sales_order"):
		return lead.get("education_auto_sales_order")

	try:
		sales_order = create_order_documents(lead)
	except Exception:
		frappe.log_error(frappe.get_traceback(), _("Auto Sales Order failed for Lead {0}").format(lead.name))
		frappe.db.set_value(
			"Lead",
			lead.name,
			{
				"education_auto_order_status": "Failed",
				"education_auto_order_error": frappe.get_traceback()[-1000:],
			},
			update_modified=False,
		)
		return None

	frappe.db.set_value(
		"Lead",
		lead.name,
		{
			"education_auto_order_status": "Completed",
			"education_auto_order_error": "",
			"education_auto_sales_order": sales_order.name,
			"education_auto_customer": sales_order.customer,
		},
		update_modified=False,
	)
	return sales_order.name


def create_order_documents(lead):
	from erpnext.crm.doctype.lead.lead import make_opportunity
	from erpnext.crm.doctype.opportunity.opportunity import make_quotation
	from erpnext.selling.doctype.quotation.quotation import make_sales_order

	company = lead.company or get_default_company()
	if not company:
		frappe.throw(_("Please set Company on Lead or configure a default Company."))

	currency = frappe.get_cached_value("Company", company, "default_currency")
	display_name = get_lead_display_name(lead)
	if lead.get("company_name") == "-" and display_name:
		lead.company_name = None
		frappe.db.set_value("Lead", lead.name, "company_name", None, update_modified=False)

	opportunity = None
	if lead.get("education_auto_opportunity"):
		opportunity = frappe.get_doc("Opportunity", lead.get("education_auto_opportunity"))
	else:
		opportunity = make_opportunity(lead.name)
		opportunity.company = company
		opportunity.currency = currency
		opportunity.customer_name = display_name
		opportunity.title = display_name
		opportunity.transaction_date = today()
		opportunity.flags.ignore_permissions = True

		opportunity.set("items", [])
		for item in lead.get("education_items"):
			opportunity.append("items", get_opportunity_item(item))

		opportunity.insert(ignore_permissions=True)
		frappe.db.set_value(
			"Lead",
			lead.name,
			"education_auto_opportunity",
			opportunity.name,
			update_modified=False,
		)

	quotation = None
	if lead.get("education_auto_quotation"):
		quotation = frappe.get_doc("Quotation", lead.get("education_auto_quotation"))
	else:
		quotation = make_quotation(opportunity.name)
		quotation.company = company
		quotation.customer_name = display_name
		quotation.transaction_date = today()
		quotation.flags.ignore_permissions = True

		for source_item, quotation_item in zip(lead.get("education_items"), quotation.get("items")):
			if source_item.warehouse and not quotation_item.warehouse:
				quotation_item.warehouse = source_item.warehouse
			
			# Sync discount and pricing
			quotation_item.discount_percentage = source_item.discount_percentage
			quotation_item.price_list_rate = source_item.price_list_rate
			quotation_item.rate = source_item.rate
			quotation_item.amount = source_item.amount

		quotation.insert(ignore_permissions=True)
		quotation.submit()
		frappe.db.set_value(
			"Lead",
			lead.name,
			"education_auto_quotation",
			quotation.name,
			update_modified=False,
		)

	sales_order = make_sales_order(quotation.name)
	sales_order.flags.ignore_permissions = True
	if display_name:
		sales_order.customer_name = display_name
	sales_order.delivery_date = nowdate()

	if sales_order.meta.has_field("education_lead"):
		sales_order.education_lead = lead.name

	for source_item, sales_order_item in zip(lead.get("education_items"), sales_order.get("items")):
		sales_order_item.delivery_date = source_item.delivery_date or nowdate()
		if source_item.warehouse and not sales_order_item.warehouse:
			sales_order_item.warehouse = source_item.warehouse

		# Sync discount and pricing
		sales_order_item.discount_percentage = source_item.discount_percentage
		sales_order_item.price_list_rate = source_item.price_list_rate
		sales_order_item.rate = source_item.rate
		sales_order_item.amount = source_item.amount

	sales_order.insert(ignore_permissions=True)
	if lead.get("education_submit_sales_order"):
		sales_order.submit()

	return sales_order


def get_opportunity_item(item):
	qty = item.qty or 1
	rate = item.rate or 0

	item_name = item.item_name
	uom = item.uom
	description = item.description

	if item.item_code and (not item_name or not uom):
		item_doc = frappe.get_cached_doc("Item", item.item_code)
		item_name = item_name or item_doc.item_name
		uom = uom or item_doc.stock_uom
		description = description or item_doc.description

	return {
		"item_code": item.item_code,
		"item_name": item_name or item.item_code or "-",
		"uom": uom or "Nos",
		"qty": qty,
		"rate": rate,
		"amount": qty * rate,
		"description": description,
		"discount_percentage": item.discount_percentage,
		"price_list_rate": item.price_list_rate,
	}


def get_default_company():
	return (
		frappe.defaults.get_user_default("Company")
		or frappe.defaults.get_global_default("company")
		or frappe.db.get_single_value("Global Defaults", "default_company")
		or frappe.db.get_value("Company", {}, "name")
	)


def set_auto_order_status(doc, status):
	if doc.get("education_auto_order_status") == status:
		return

	if doc.is_new():
		doc.education_auto_order_status = status
		return

	frappe.db.set_value("Lead", doc.name, "education_auto_order_status", status, update_modified=False)
