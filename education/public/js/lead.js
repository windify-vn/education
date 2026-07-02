frappe.ui.form.on("Lead", {
	setup(frm) {
		education_patch_lead_meta();
	},

	refresh(frm) {
		education_patch_lead_meta();

		if (frm.doc.education_auto_sales_order) {
			frm.add_custom_button(__("Open Sales Order"), () => {
				frappe.set_route("Form", "Sales Order", frm.doc.education_auto_sales_order);
			});
			return;
		}

		if (frm.doc.education_auto_order_status === "Queued") {
			education_start_sales_order_poll(frm);
		}
	},

	before_save(frm) {
		// Safety net: fill Lead mandatory fields synchronously before Frappe checks them
		if (frm.doc.education_student_full_name) {
			frm.doc.lead_name = frm.doc.education_student_full_name;
		}
		if (!frm.doc.first_name) {
			frm.doc.first_name = (
				frm.doc.education_student_full_name
				|| frm.doc.lead_name
				|| frm.doc.email_id
				|| frm.doc.mobile_no
				|| "-"
			);
		}
		if (frm.doc.company_name === "-") {
			frm.doc.company_name = "";
		}

		// Auto-calculate amount for each items row
		(frm.doc.education_items || []).forEach((row) => {
			const qty = row.qty || 1;
			let price_list_rate = row.price_list_rate || 0;
			const discount = row.discount_percentage || 0;
			
			// Tính rate nếu có discount
			let rate = row.rate || 0;
			if (discount > 0 && price_list_rate > 0) {
				rate = price_list_rate * (1 - discount / 100.0);
				row.rate = rate;
			} else if (!row.rate) {
				rate = price_list_rate;
				row.rate = rate;
			}

			const conversion_factor = row.conversion_factor || 1;
			const amount = qty * rate;
			
			row.conversion_factor = conversion_factor;
			row.stock_qty = qty * conversion_factor;
			row.amount = amount;
			row.base_rate = row.base_rate || rate;
			row.base_amount = row.base_amount || amount;
		});
	},

	after_save(frm) {
		education_start_sales_order_poll(frm);
	},
});

function education_patch_lead_meta() {
	// Remove mandatory from Lead's first_name and company_name in client-side meta
	["first_name", "company_name"].forEach((fieldname) => {
		const df = frappe.meta.get_docfield("Lead", fieldname);
		if (df) {
			df.reqd = 0;
			df.mandatory_depends_on = "";
		}
	});
}

function education_start_sales_order_poll(frm) {
	if (
		frm.is_new()
		|| frm.__education_auto_order_polling
		|| !frm.doc.education_auto_create_sales_order
		|| frm.doc.education_auto_sales_order
		|| !(frm.doc.education_items || []).length
	) {
		return;
	}

	frm.__education_auto_order_polling = true;
	frappe.show_alert({
		message: __("Creating Sales Order in the background..."),
		indicator: "blue",
	});

	let attempts = 0;
	const max_attempts = 40;
	const poll = () => {
		attempts += 1;

		frappe.db
			.get_value("Lead", frm.doc.name, [
				"education_auto_order_status",
				"education_auto_sales_order",
				"education_auto_order_error",
			])
			.then((response) => {
				const values = response.message || {};

				if (values.education_auto_sales_order) {
					frm.__education_auto_order_polling = false;
					frm.set_value("education_auto_sales_order", values.education_auto_sales_order);
					frm.set_value("education_auto_order_status", values.education_auto_order_status);

					frappe.show_alert({
						message: __("Sales Order created. Opening it for review..."),
						indicator: "green",
					});

					setTimeout(() => {
						frappe.set_route("Form", "Sales Order", values.education_auto_sales_order);
					}, 700);
					return;
				}

				if (values.education_auto_order_status === "Failed") {
					frm.__education_auto_order_polling = false;
					frappe.msgprint({
						title: __("Sales Order creation failed"),
						indicator: "red",
						message: values.education_auto_order_error || __("Please check Error Log."),
					});
					return;
				}

				if (attempts < max_attempts) {
					setTimeout(poll, 1500);
				} else {
					frm.__education_auto_order_polling = false;
					frappe.show_alert({
						message: __("Sales Order is still being created. Refresh this Lead in a moment."),
						indicator: "orange",
					});
				}
			});
	};

	setTimeout(poll, 1000);
}
