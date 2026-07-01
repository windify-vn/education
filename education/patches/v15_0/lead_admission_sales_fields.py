import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from education.install import apply_lead_property_setters, get_custom_fields


def execute():
	custom_fields = get_custom_fields()
	create_custom_fields(
		{
			"Lead": custom_fields["Lead"],
			"Sales Order": custom_fields["Sales Order"],
		}
	)
	apply_final_lead_field_settings()
	migrate_existing_lead_items()
	apply_lead_property_setters()
	repair_existing_education_lead_titles()
	frappe.clear_cache(doctype="Lead")
	frappe.clear_cache(doctype="Sales Order")
	frappe.db.updatedb("Lead")
	frappe.db.updatedb("Sales Order")


def apply_final_lead_field_settings():
	set_custom_field_values(
		"Lead-education_items",
		{
			"fieldtype": "Table",
			"options": "Sales Order Item",
			"reqd": 1,
		},
	)
	set_custom_field_values(
		"Lead-education_grade_class",
		{
			"fieldtype": "Data",
			"options": None,
		},
	)
	set_custom_field_values(
		"Lead-education_campaign",
		{
			"fieldtype": "Link",
			"options": "UTM Campaign",
			"reqd": 1,
		},
	)


def set_custom_field_values(custom_field, values):
	if frappe.db.exists("Custom Field", custom_field):
		frappe.db.set_value("Custom Field", custom_field, values, update_modified=False)


def migrate_existing_lead_items():
	if not (
		frappe.db.table_exists("Education Lead Item")
		and frappe.db.table_exists("Sales Order Item")
	):
		return

	existing_sales_order_item_parents = set(
		frappe.get_all(
			"Sales Order Item",
			filters={"parenttype": "Lead", "parentfield": "education_items"},
			pluck="parent",
		)
	)

	lead_items = frappe.get_all(
		"Education Lead Item",
		filters={"parenttype": "Lead", "parentfield": "education_items"},
		fields=[
			"parent",
			"idx",
			"item_code",
			"item_name",
			"qty",
			"uom",
			"rate",
			"delivery_date",
			"warehouse",
			"description",
		],
		order_by="parent asc, idx asc",
	)

	for lead_item in lead_items:
		if lead_item.parent in existing_sales_order_item_parents:
			continue
		if not lead_item.item_code:
			continue

		item_defaults = get_item_defaults(lead_item.item_code)
		qty = lead_item.qty or 1
		rate = lead_item.rate or 0
		amount = qty * rate
		stock_uom = item_defaults.get("stock_uom")
		uom = lead_item.uom or stock_uom
		conversion_factor = 1

		frappe.get_doc(
			{
				"doctype": "Sales Order Item",
				"parent": lead_item.parent,
				"parenttype": "Lead",
				"parentfield": "education_items",
				"idx": lead_item.idx,
				"item_code": lead_item.item_code,
				"item_name": lead_item.item_name or item_defaults.get("item_name"),
				"description": lead_item.description or item_defaults.get("description"),
				"qty": qty,
				"uom": uom,
				"stock_uom": stock_uom or uom,
				"conversion_factor": conversion_factor,
				"stock_qty": qty * conversion_factor,
				"rate": rate,
				"amount": amount,
				"base_rate": rate,
				"base_amount": amount,
				"delivery_date": lead_item.delivery_date,
				"warehouse": lead_item.warehouse,
			}
		).insert(ignore_permissions=True)


def get_item_defaults(item_code):
	if not item_code:
		return {}

	return frappe.db.get_value(
		"Item",
		item_code,
		["item_name", "stock_uom", "description"],
		as_dict=True,
	) or {}


def repair_existing_education_lead_titles():
	frappe.db.sql(
		"""
		update `tabOpportunity` opportunity
		join `tabLead` lead on lead.education_auto_opportunity = opportunity.name
		set
			opportunity.customer_name = lead.education_student_full_name,
			opportunity.title = lead.education_student_full_name
		where lead.company_name = '-'
			and ifnull(lead.education_student_full_name, '') != ''
		"""
	)
	frappe.db.sql(
		"""
		update `tabQuotation` quotation
		join `tabLead` lead on lead.education_auto_quotation = quotation.name
		set quotation.customer_name = lead.education_student_full_name
		where lead.company_name = '-'
			and ifnull(lead.education_student_full_name, '') != ''
		"""
	)
	frappe.db.sql(
		"""
		update `tabSales Order` sales_order
		join `tabLead` lead on lead.education_auto_sales_order = sales_order.name
		set sales_order.customer_name = lead.education_student_full_name
		where lead.company_name = '-'
			and ifnull(lead.education_student_full_name, '') != ''
		"""
	)
	frappe.db.sql(
		"""
		update `tabCustomer` customer
		join `tabLead` lead on customer.lead_name = lead.name
		set
			customer.customer_name = lead.education_student_full_name,
			customer.customer_type = 'Individual'
		where lead.company_name = '-'
			and customer.customer_name = '-'
			and ifnull(lead.education_student_full_name, '') != ''
		"""
	)
	frappe.db.sql(
		"""
		update `tabLead`
		set
			company_name = null,
			title = education_student_full_name,
			lead_name = education_student_full_name
		where company_name = '-'
			and ifnull(education_student_full_name, '') != ''
		"""
	)
