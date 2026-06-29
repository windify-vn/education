from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from education.install import apply_lead_property_setters, get_custom_fields


def execute():
	create_custom_fields({"Lead": get_custom_fields()["Lead"]})
	apply_lead_property_setters()
