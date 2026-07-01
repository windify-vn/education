# Copyright (c) 2026, Windify Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.utils import today


def on_submit(doc, method=None):
	create_student_profile(doc)


def create_student_profile(sales_order):
	lead = get_source_lead(sales_order)
	if not lead:
		return

	student = sales_order.get("student")
	if not student:
		student = create_student_from_lead(lead, sales_order)

	guardian = get_or_create_guardian_from_lead(lead)
	if guardian:
		link_guardian_to_student(student, guardian, lead.get("education_parent_relationship"))

	update_sales_order_links(sales_order, lead.name, student, guardian)


def get_source_lead(sales_order):
	lead_name = sales_order.get("education_lead") or get_source_lead_name(sales_order)
	if not lead_name or not frappe.db.exists("Lead", lead_name):
		return None

	return frappe.get_doc("Lead", lead_name)


def get_source_lead_name(sales_order):
	lead_name = frappe.db.get_value("Lead", {"education_auto_sales_order": sales_order.name})
	if lead_name:
		return lead_name

	quotation = get_source_quotation(sales_order)
	if not quotation:
		return None

	lead_name = frappe.db.get_value("Lead", {"education_auto_quotation": quotation})
	if lead_name:
		return lead_name

	quotation_doc = frappe.get_doc("Quotation", quotation)
	if quotation_doc.get("quotation_to") == "Lead" and quotation_doc.get("party_name"):
		return quotation_doc.get("party_name")

	opportunity = quotation_doc.get("opportunity") or get_source_opportunity_from_quotation(quotation_doc)
	if not opportunity:
		return None

	opportunity_doc = frappe.get_doc("Opportunity", opportunity)
	if opportunity_doc.get("opportunity_from") == "Lead":
		return opportunity_doc.get("party_name")

	return None


def get_source_quotation(sales_order):
	for item in sales_order.get("items"):
		if item.get("prevdoc_docname"):
			return item.get("prevdoc_docname")

	return None


def get_source_opportunity_from_quotation(quotation):
	for item in quotation.get("items"):
		if item.get("prevdoc_doctype") == "Opportunity" and item.get("prevdoc_docname"):
			return item.get("prevdoc_docname")

	return None


def create_student_from_lead(lead, sales_order):
	from erpnext.selling.doctype.customer.customer import parse_full_name

	full_name = lead.get("education_student_full_name") or lead.get("lead_name")
	if not full_name:
		frappe.throw(_("Student Full Name is required on Lead {0}.").format(lead.name))

	first_name, middle_name, last_name = parse_full_name(full_name)
	if not first_name:
		frappe.throw(_("Could not parse Student Full Name on Lead {0}.").format(lead.name))

	student_doc = frappe.get_doc(
		{
			"doctype": "Student",
			"first_name": first_name,
			"middle_name": middle_name,
			"last_name": last_name,
			"student_email_id": get_student_email(lead, sales_order),
			"date_of_birth": lead.get("education_date_of_birth"),
			"gender": lead.get("gender"),
			"joining_date": today(),
			"customer": sales_order.get("customer"),
		}
	)

	mute_emails, in_import = frappe.flags.mute_emails, frappe.flags.in_import
	frappe.flags.mute_emails = True
	frappe.flags.in_import = True
	try:
		student_doc.insert(ignore_permissions=True)
	finally:
		frappe.flags.mute_emails = mute_emails
		frappe.flags.in_import = in_import

	return student_doc.name


def get_student_email(lead, sales_order):
	parent_email = lead.get("education_parent_email") or lead.get("email_id")
	if parent_email and not frappe.db.exists("Student", {"student_email_id": parent_email}):
		return parent_email

	return get_internal_student_email(sales_order.name)


def get_internal_student_email(sales_order_name):
	safe_name = re.sub(r"[^a-z0-9]+", "-", sales_order_name.lower()).strip("-")
	base_email = f"student-{safe_name}@education.local"
	email = base_email
	counter = 1

	while frappe.db.exists("Student", {"student_email_id": email}) or frappe.db.exists("User", email):
		counter += 1
		email = f"student-{safe_name}-{counter}@education.local"

	return email


def get_or_create_guardian_from_lead(lead):
	parent_name = lead.get("education_parent_full_name")
	parent_phone = lead.get("education_parent_phone_number")
	parent_email = lead.get("education_parent_email")

	if not (parent_name or parent_phone or parent_email):
		return None

	guardian = None
	if parent_phone:
		guardian = frappe.db.get_value("Guardian", {"mobile_number": parent_phone})

	if not guardian and parent_email:
		guardian = frappe.db.get_value("Guardian", {"email_address": parent_email})

	if guardian:
		update_guardian_if_missing(guardian, parent_name, parent_phone, parent_email)
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


def update_guardian_if_missing(guardian, parent_name=None, parent_phone=None, parent_email=None):
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


def link_guardian_to_student(student, guardian, relationship=None):
	student_doc = frappe.get_doc("Student", student)
	for row in student_doc.get("guardians"):
		if row.guardian != guardian:
			continue

		if relationship and not row.relation:
			row.relation = relationship
			student_doc.save(ignore_permissions=True)
		return

	student_doc.append(
		"guardians",
		{
			"guardian": guardian,
			"relation": relationship,
		},
	)
	student_doc.save(ignore_permissions=True)


def update_sales_order_links(sales_order, lead, student, guardian=None):
	values = {}

	if sales_order.meta.has_field("education_lead") and not sales_order.get("education_lead"):
		values["education_lead"] = lead
	if sales_order.meta.has_field("student") and sales_order.get("student") != student:
		values["student"] = student
	if guardian and sales_order.meta.has_field("education_guardian"):
		values["education_guardian"] = guardian

	if values:
		frappe.db.set_value("Sales Order", sales_order.name, values, update_modified=False)
		sales_order.update(values)
