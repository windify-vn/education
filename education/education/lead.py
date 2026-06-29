# Copyright (c) 2026, Windify Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, today


def before_validate(doc, method=None):
	sync_employee_owner(doc)
	sync_campaign(doc)
	sync_parent_contact_to_lead(doc)


def validate(doc, method=None):
	ensure_guardian(doc)


def after_insert(doc, method=None):
	queue_auto_sales_order(doc)


def on_update(doc, method=None):
	ensure_guardian(doc)
	queue_auto_sales_order(doc)


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


def ensure_guardian(doc):
	parent_name = doc.get("education_parent_full_name")
	parent_phone = doc.get("education_parent_phone_number")
	parent_email = doc.get("education_parent_email")

	if not (parent_name or parent_phone or parent_email):
		return

	guardian = get_or_create_guardian(parent_name, parent_phone, parent_email)
	if not guardian:
		return

	if doc.get("education_guardian") != guardian:
		doc.education_guardian = guardian
		if not doc.is_new():
			frappe.db.set_value("Lead", doc.name, "education_guardian", guardian, update_modified=False)

	link_guardian_to_student(doc, guardian)


def get_or_create_guardian(parent_name=None, parent_phone=None, parent_email=None):
	guardian = None

	if parent_phone:
		guardian = frappe.db.get_value("Guardian", {"mobile_number": parent_phone})

	if not guardian and parent_email:
		guardian = frappe.db.get_value("Guardian", {"email_address": parent_email})

	if guardian:
		guardian_doc = frappe.get_doc("Guardian", guardian)
		changed = False

		if parent_name and not guardian_doc.guardian_name:
			guardian_doc.guardian_name = parent_name
			changed = True
		if parent_email and not guardian_doc.email_address:
			guardian_doc.email_address = parent_email
			changed = True
		if parent_phone and not guardian_doc.mobile_number:
			guardian_doc.mobile_number = parent_phone
			changed = True

		if changed:
			guardian_doc.save(ignore_permissions=True)

		return guardian

	if not parent_name:
		parent_name = parent_phone or parent_email

	guardian_doc = frappe.get_doc(
		{
			"doctype": "Guardian",
			"guardian_name": parent_name,
			"mobile_number": parent_phone,
			"email_address": parent_email,
		}
	)
	guardian_doc.insert(ignore_permissions=True)
	return guardian_doc.name


def link_guardian_to_student(doc, guardian):
	student = doc.get("education_student")
	if not student:
		return

	student_doc = frappe.get_doc("Student", student)
	for row in student_doc.get("guardians"):
		if row.guardian == guardian:
			if doc.get("education_parent_relationship") and not row.relation:
				row.relation = doc.get("education_parent_relationship")
				student_doc.save(ignore_permissions=True)
			return

	student_doc.append(
		"guardians",
		{
			"guardian": guardian,
			"relation": doc.get("education_parent_relationship"),
		},
	)
	student_doc.save(ignore_permissions=True)


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

	opportunity = None
	if lead.get("education_auto_opportunity"):
		opportunity = frappe.get_doc("Opportunity", lead.get("education_auto_opportunity"))
	else:
		opportunity = make_opportunity(lead.name)
		opportunity.company = company
		opportunity.currency = currency
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
		quotation.transaction_date = today()
		quotation.flags.ignore_permissions = True

		for source_item, quotation_item in zip(lead.get("education_items"), quotation.get("items")):
			if source_item.warehouse and not quotation_item.warehouse:
				quotation_item.warehouse = source_item.warehouse

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
	sales_order.delivery_date = lead.get("education_delivery_date") or nowdate()

	if sales_order.meta.has_field("student") and lead.get("education_student"):
		sales_order.student = lead.get("education_student")

	for source_item, sales_order_item in zip(lead.get("education_items"), sales_order.get("items")):
		sales_order_item.delivery_date = (
			source_item.delivery_date or lead.get("education_delivery_date") or nowdate()
		)
		if source_item.warehouse and not sales_order_item.warehouse:
			sales_order_item.warehouse = source_item.warehouse

	sales_order.insert(ignore_permissions=True)
	if lead.get("education_submit_sales_order"):
		sales_order.submit()

	return sales_order


def get_opportunity_item(item):
	item_doc = frappe.get_cached_doc("Item", item.item_code)
	qty = item.qty or 1
	rate = item.rate or 0

	return {
		"item_code": item.item_code,
		"item_name": item.item_name or item_doc.item_name,
		"uom": item.uom or item_doc.stock_uom,
		"qty": qty,
		"rate": rate,
		"amount": qty * rate,
		"description": item.description or item_doc.description,
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
