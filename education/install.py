import json

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import (
	delete_property_setter,
	make_property_setter,
)
from frappe.desk.page.setup_wizard.setup_wizard import make_records
from frappe.permissions import add_permission, update_permission_property


def after_install():
	setup_fixtures()
	create_student_role()
	create_parent_assessment_group()
	create_invoice_permissions()
	create_custom_fields(get_custom_fields())
	apply_lead_property_setters()
	create_permissions(get_permissions())


def setup_fixtures():
	records = [
		# Party Type Records
		{"doctype": "Party Type", "party_type": "Student", "account_type": "Receivable"},
		# Item Group Records
		{"doctype": "Item Group", "item_group_name": "Fee Component"},
		# Customer Group Records
		{"doctype": "Customer Group", "customer_group_name": "Student"},
	]
	make_records(records)


def create_parent_assessment_group():
	if not frappe.db.exists("Assessment Group", "All Assessment Groups"):
		frappe.get_doc(
			{
				"doctype": "Assessment Group",
				"assessment_group_name": "All Assessment Groups",
				"is_group": 1,
			}
		).insert(ignore_mandatory=True)


def create_student_role():
	if not frappe.db.exists("Role", "Student"):
		frappe.get_doc({"doctype": "Role", "role_name": "Student", "desk_access": 0}).save()


def create_invoice_permissions():
	add_permission("Sales Invoice", "Student", 0)

	doctype = "Sales Invoice"
	role = "Student"
	permlevel = 0
	ptype = ["read", "write", "print"]

	for p in ptype:
		# update permissions
		update_permission_property(doctype, role, permlevel, p, 1)


def get_permissions():
	return [
		{
			"doctype": "Sales Invoice",
			"role": "Student",
			"permlevel": 0,
			"ptype": ["read", "write", "print"],
		},
		{
			"doctype": "User",
			"role": "Academics User",
			"permlevel": 0,
			"ptype": ["read", "write", "create"],
		},
		{
			"doctype": "Customer",
			"role": "Academics User",
			"permlevel": 0,
			"ptype": ["read", "write", "create"],
		},
	]


def create_permissions(doctype_permissions):
	for doctype_permission in doctype_permissions:
		doctype = doctype_permission.get("doctype")
		role = doctype_permission.get("role")
		permlevel = doctype_permission.get("permlevel")
		ptype = doctype_permission.get("ptype")
		add_permission(doctype, role, permlevel)
		for p in ptype:
			update_permission_property(doctype, role, permlevel, p, 1)


def get_custom_fields():
	"""Education specific custom fields added to ERPNext DocTypes."""
	return {
		"Lead": [
			{
				"fieldname": "education_general_information",
				"fieldtype": "Section Break",
				"label": "Student Information",
				"insert_after": "naming_series",
			},
			{
				"fieldname": "education_student_full_name",
				"fieldtype": "Data",
				"label": "Full Name",
				"reqd": 1,
				"insert_after": "education_general_information",
			},
			{
				"fieldname": "education_date_of_birth",
				"fieldtype": "Date",
				"label": "Date of Birth",
				"reqd": 1,
				"insert_after": "education_general_column_break",
			},
			{
				"fieldname": "education_grade_class",
				"fieldtype": "Data",
				"label": "Grade / Class",
				"insert_after": "gender",
			},
			{
				"fieldname": "education_interest_level",
				"fieldtype": "Select",
				"label": "Mức độ quan tâm",
				"options": "\nRất quan tâm\nQuan tâm\nTrung bình\nÍt quan tâm",
				"insert_after": "education_grade_class",
			},
			{
				"fieldname": "education_general_column_break",
				"fieldtype": "Column Break",
				"insert_after": "education_interest_level",
			},
			{
				"fieldname": "education_lead_owner_employee",
				"fieldtype": "Link",
				"label": "Lead Owner (responsible sales person)",
				"options": "Employee",
				"reqd": 1,
				"insert_after": "education_date_of_birth",
			},
			{
				"fieldname": "education_address",
				"fieldtype": "Small Text",
				"label": "Address",
				"insert_after": "education_lead_owner_employee",
			},
			{
				"fieldname": "education_parent_information",
				"fieldtype": "Section Break",
				"label": "Parent Information",
				"insert_after": "phone_ext",
			},
			{
				"fieldname": "education_parent_full_name",
				"fieldtype": "Data",
				"label": "Full Name",
				"reqd": 1,
				"insert_after": "education_parent_information",
			},
			{
				"fieldname": "education_parent_phone_number",
				"fieldtype": "Data",
				"label": "Phone Number",
				"options": "Phone",
				"reqd": 1,
				"insert_after": "education_parent_column_break",
			},
			{
				"fieldname": "education_parent_column_break",
				"fieldtype": "Column Break",
				"insert_after": "education_parent_email",
			},
			{
				"fieldname": "education_parent_email",
				"fieldtype": "Data",
				"label": "Email",
				"options": "Email",
				"insert_after": "education_parent_full_name",
			},
			{
				"fieldname": "education_parent_relationship",
				"fieldtype": "Select",
				"label": "Relationship",
				"options": "\nMother\nFather\nOthers",
				"reqd": 1,
				"insert_after": "education_parent_phone_number",
			},
			{
				"fieldname": "education_guardian",
				"fieldtype": "Link",
				"label": "Guardian",
				"options": "Guardian",
				"read_only": 1,
				"insert_after": "education_parent_relationship",
			},
			{
				"fieldname": "education_course_source_information",
				"fieldtype": "Section Break",
				"label": "Course & Source Information",
				"insert_after": "education_guardian",
			},
			{
				"fieldname": "education_items",
				"fieldtype": "Table",
				"label": "Items",
				"options": "Sales Order Item",
				"reqd": 1,
				"insert_after": "education_course_source_information",
			},
			{
				"fieldname": "education_campaign",
				"fieldtype": "Link",
				"label": "Campaign",
				"options": "UTM Campaign",
				"reqd": 1,
				"insert_after": "education_items",
			},
			{
				"fieldname": "education_auto_order_section",
				"fieldtype": "Section Break",
				"hidden": 1,
				"label": "Auto Sales Order",
				"collapsible": 1,
				"insert_after": "education_campaign",
			},
			{
				"default": "1",
				"fieldname": "education_auto_create_sales_order",
				"fieldtype": "Check",
				"hidden": 1,
				"label": "Auto Create Sales Order",
				"insert_after": "education_auto_order_section",
			},
			{
				"default": "0",
				"fieldname": "education_submit_sales_order",
				"fieldtype": "Check",
				"hidden": 1,
				"label": "Submit Sales Order Automatically",
				"insert_after": "education_auto_create_sales_order",
			},
			{
				"fieldname": "education_auto_order_status",
				"fieldtype": "Select",
				"hidden": 1,
				"label": "Auto Order Status",
				"options": "\nPending\nSkipped\nQueued\nCompleted\nFailed",
				"read_only": 1,
				"insert_after": "education_submit_sales_order",
			},
			{
				"fieldname": "education_auto_order_column_break",
				"fieldtype": "Column Break",
				"hidden": 1,
				"insert_after": "education_auto_order_status",
			},
			{
				"fieldname": "education_auto_opportunity",
				"fieldtype": "Link",
				"hidden": 1,
				"label": "Opportunity",
				"options": "Opportunity",
				"read_only": 1,
				"insert_after": "education_auto_order_column_break",
			},
			{
				"fieldname": "education_auto_quotation",
				"fieldtype": "Link",
				"hidden": 1,
				"label": "Quotation",
				"options": "Quotation",
				"read_only": 1,
				"insert_after": "education_auto_opportunity",
			},
			{
				"fieldname": "education_auto_sales_order",
				"fieldtype": "Link",
				"hidden": 1,
				"label": "Sales Order",
				"options": "Sales Order",
				"read_only": 1,
				"insert_after": "education_auto_quotation",
			},
			{
				"fieldname": "education_auto_customer",
				"fieldtype": "Link",
				"hidden": 1,
				"label": "Customer",
				"options": "Customer",
				"read_only": 1,
				"insert_after": "education_auto_sales_order",
			},
			{
				"fieldname": "education_auto_order_error",
				"fieldtype": "Small Text",
				"hidden": 1,
				"label": "Auto Order Error",
				"read_only": 1,
				"insert_after": "education_auto_customer",
			},
		],
		"Sales Invoice": [
			{
				"fieldname": "student_info_section",
				"fieldtype": "Section Break",
				"label": "Student Info",
				"collapsible": 1,
				"insert_after": "ignore_pricing_rule",
			},
			{
				"fieldname": "student",
				"fieldtype": "Link",
				"label": "Student",
				"options": "Student",
				"insert_after": "student_info_section",
			},
			{
				"fieldname": "column_break_ejcc",
				"fieldtype": "Column Break",
				"insert_after": "student",
			},
			{
				"fieldname": "fee_schedule",
				"fieldtype": "Link",
				"label": "Fee Schedule",
				"options": "Fee Schedule",
				"insert_after": "column_break_ejcc",
			},
		],
		"Sales Order": [
			{
				"fieldname": "student_info_section",
				"fieldtype": "Section Break",
				"label": "Student Info",
				"collapsible": 1,
				"insert_after": "ignore_pricing_rule",
			},
			{
				"fieldname": "education_lead",
				"fieldtype": "Link",
				"label": "Lead",
				"options": "Lead",
				"read_only": 1,
				"insert_after": "student_info_section",
			},
			{
				"fieldname": "student",
				"fieldtype": "Link",
				"label": "Student",
				"options": "Student",
				"insert_after": "education_lead",
			},
			{
				"fieldname": "education_guardian",
				"fieldtype": "Link",
				"label": "Guardian",
				"options": "Guardian",
				"read_only": 1,
				"insert_after": "student",
			},
			{
				"fieldname": "column_break_ejcc",
				"fieldtype": "Column Break",
				"insert_after": "education_guardian",
			},
			{
				"fieldname": "fee_schedule",
				"fieldtype": "Link",
				"label": "Fee Schedule",
				"options": "Fee Schedule",
				"insert_after": "column_break_ejcc",
			},
		],
	}


def apply_lead_property_setters():
	delete_removed_lead_custom_fields()

	for fieldname in get_core_lead_fields():
		hidden = 0 if fieldname == "gender" else 1
		make_property_setter(
			"Lead",
			fieldname,
			"hidden",
			hidden,
			"Check",
			validate_fields_for_doctype=False,
		)

	make_property_setter(
		"Lead",
		"education_items",
		"allow_bulk_edit",
		1,
		"Check",
		validate_fields_for_doctype=False,
	)

	# Remove mandatory from core Lead fields (not needed for education leads)
	for fieldname in ("first_name", "company_name"):
		make_property_setter(
			"Lead",
			fieldname,
			"reqd",
			0,
			"Check",
			validate_fields_for_doctype=False,
		)

	delete_property_setter("Lead", "insert_after", "gender")
	apply_lead_field_order()


def apply_lead_field_order():
	lead_fieldnames = [df.fieldname for df in frappe.get_meta("Lead", cached=False).fields]
	field_order = []

	for fieldname in get_priority_lead_fields():
		if fieldname in lead_fieldnames and fieldname not in field_order:
			field_order.append(fieldname)

	for fieldname in lead_fieldnames:
		if fieldname not in field_order:
			field_order.append(fieldname)

	make_property_setter(
		"Lead",
		None,
		"field_order",
		json.dumps(field_order),
		"Text",
		for_doctype=True,
		validate_fields_for_doctype=False,
	)
	frappe.clear_cache(doctype="Lead")


def get_priority_lead_fields():
	return [
		"naming_series",
		"education_general_information",
		"education_student_full_name",
		"gender",
		"education_grade_class",
		"education_interest_level",
		"education_general_column_break",
		"education_date_of_birth",
		"education_lead_owner_employee",
		"education_address",
		"education_parent_information",
		"education_parent_full_name",
		"education_parent_email",
		"education_parent_column_break",
		"education_parent_phone_number",
		"education_parent_relationship",
		"education_guardian",
		"education_course_source_information",
		"education_items",
		"education_campaign",
		"education_auto_order_section",
		"education_auto_create_sales_order",
		"education_submit_sales_order",
		"education_auto_order_status",
		"education_auto_order_column_break",
		"education_auto_opportunity",
		"education_auto_quotation",
		"education_auto_sales_order",
		"education_auto_customer",
		"education_auto_order_error",
	]


def get_core_lead_fields():
	return [
		"naming_series",
		"salutation",
		"first_name",
		"middle_name",
		"last_name",
		"column_break_1",
		"col_break123",
		"lead_name",
		"job_title",
		"gender",
		"lead_owner",
		"status",
		"customer",
		"type",
		"request_type",
		"contact_info_tab",
		"email_id",
		"website",
		"column_break_20",
		"mobile_no",
		"whatsapp_no",
		"column_break_16",
		"phone",
		"phone_ext",
		"organization_section",
		"company_name",
		"no_of_employees",
		"column_break_28",
		"annual_revenue",
		"industry",
		"market_segment",
		"column_break_31",
		"territory",
		"fax",
		"address_section",
		"address_html",
		"column_break_38",
		"column_break2",
		"contact_html",
		"city",
		"state",
		"country",
		"section_break_analytics",
		"utm_source",
		"utm_content",
		"column_break_gkxo",
		"utm_campaign",
		"column_break_gqka",
		"utm_medium",
		"qualification_tab",
		"qualification_status",
		"column_break_64",
		"qualified_by",
		"qualified_on",
		"other_info_tab",
		"company",
		"column_break_22",
		"language",
		"image",
		"title",
		"column_break_50",
		"disabled",
		"unsubscribed",
		"blog_subscriber",
		"activities_tab",
		"open_activities_html",
		"all_activities_section",
		"all_activities_html",
		"notes_tab",
		"notes_html",
		"notes",
		"dashboard_tab",
	]


def delete_removed_lead_custom_fields():
	for custom_field in (
		"Lead-education_student",
		"Lead-education_delivery_date",
		"Lead-education_course_source_column_break",
		"Lead-education_parent_second_row",
		"Lead-education_parent_relationship_column_break",
		"Lead-education_campaign_row",
	):
		if not frappe.db.exists("Custom Field", custom_field):
			continue

		frappe.delete_doc(
			"Custom Field",
			custom_field,
			ignore_permissions=True,
			force=True,
		)
