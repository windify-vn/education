frappe.listview_settings["Lead"] = frappe.listview_settings["Lead"] || {};

(function () {
	const _orig_onload = frappe.listview_settings["Lead"].onload;

	frappe.listview_settings["Lead"].onload = function (listview) {
		if (_orig_onload) _orig_onload(listview);

		listview.page.add_inner_button(__("Xuất bảng theo dõi doanh số"), function () {
			education_show_sales_report_dialog();
		});

		listview.page.add_inner_button(__("Thống kê khách hàng"), function () {
			education_show_customer_statistics_dialog();
		});
	};
})();

function education_show_sales_report_dialog() {
	const today = new Date();
	const month = today.getMonth() + 1; // 1-12
	const year = today.getFullYear();

	const d = new frappe.ui.Dialog({
		title: __("Xuất bảng theo dõi doanh số"),
		fields: [
			{
				fieldtype: "Int",
				fieldname: "month",
				label: __("Tháng (1-12)"),
				default: month,
				reqd: 1,
			},
			{
				fieldtype: "Int",
				fieldname: "year",
				label: __("Năm"),
				default: year,
				reqd: 1,
			},
		],
		primary_action_label: __("Xuất Excel"),
		primary_action(values) {
			d.hide();
			education_download_sales_report(values.month, values.year);
		},
	});

	d.show();
}

function education_download_sales_report(month, year) {
	const loading = frappe.show_alert({
		message: __("Đang tạo báo cáo..."),
		indicator: "blue",
	});

	const params = new URLSearchParams({
		cmd: "education.education.lead_report.export_lead_sales_report",
		month: month,
		year: year,
	});

	// Use fetch to get the file, then trigger download
	fetch(`/api/method/education.education.lead_report.export_lead_sales_report`, {
		method: "POST",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded",
			"X-Frappe-CSRF-Token": frappe.csrf_token,
		},
		body: params.toString(),
	})
		.then((response) => {
			if (!response.ok) {
				return response.json().then((data) => {
					const msg =
						(data._server_messages && JSON.parse(data._server_messages)[0]) ||
						data.exception ||
						__("Không thể tạo báo cáo.");
					frappe.msgprint({ title: __("Lỗi"), message: msg, indicator: "red" });
					throw new Error(msg);
				});
			}

			const disposition = response.headers.get("Content-Disposition") || "";
			const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
			const filename = match
				? match[1].replace(/['"]/g, "")
				: `lead_sales_report_${year}_${String(month).padStart(2, "0")}.xlsx`;

			return response.blob().then((blob) => ({ blob, filename }));
		})
		.then(({ blob, filename }) => {
			const url = URL.createObjectURL(blob);
			const a = document.createElement("a");
			a.href = url;
			a.download = filename;
			document.body.appendChild(a);
			a.click();
			setTimeout(() => {
				URL.revokeObjectURL(url);
				document.body.removeChild(a);
			}, 500);

			frappe.show_alert({
				message: __("Đã xuất báo cáo thành công."),
				indicator: "green",
			});
		})
		.catch((err) => {
			console.error("Sales report export failed:", err);
		});
}

function education_show_customer_statistics_dialog() {
	const today = frappe.datetime.get_today();
	const monthStart = frappe.datetime.month_start(today);

	const d = new frappe.ui.Dialog({
		title: __("Thống kê khách hàng"),
		fields: [
			{
				fieldtype: "Date",
				fieldname: "from_date",
				label: __("Từ ngày"),
				default: monthStart,
				reqd: 1,
			},
			{
				fieldtype: "Date",
				fieldname: "to_date",
				label: __("Đến ngày"),
				default: today,
				reqd: 1,
			},
		],
		primary_action_label: __("Xuất Excel"),
		primary_action(values) {
			if (values.from_date > values.to_date) {
				frappe.msgprint({
					title: __("Ngày không hợp lệ"),
					message: __("Từ ngày không được lớn hơn Đến ngày."),
					indicator: "red",
				});
				return;
			}

			d.hide();
			education_download_customer_statistics(values.from_date, values.to_date);
		},
	});

	d.show();
}

function education_download_customer_statistics(from_date, to_date) {
	frappe.show_alert({
		message: __("Đang tạo thống kê khách hàng..."),
		indicator: "blue",
	});

	fetch(`/api/method/education.education.lead_report.export_customer_statistics`, {
		method: "POST",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded",
			"X-Frappe-CSRF-Token": frappe.csrf_token,
		},
		body: new URLSearchParams({
			cmd: "education.education.lead_report.export_customer_statistics",
			from_date: from_date,
			to_date: to_date,
		}).toString(),
	})
		.then((response) => {
			if (!response.ok) {
				return response.json().then((data) => {
					const msg =
						(data._server_messages && JSON.parse(data._server_messages)[0]) ||
						data.exception ||
						__("Không thể tạo thống kê khách hàng.");
					frappe.msgprint({ title: __("Lỗi"), message: msg, indicator: "red" });
					throw new Error(msg);
				});
			}

			const disposition = response.headers.get("Content-Disposition") || "";
			const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
			const filename = match
				? match[1].replace(/['"]/g, "")
				: `thong_ke_khach_hang_${from_date}_${to_date}.xlsx`;

			return response.blob().then((blob) => ({ blob, filename }));
		})
		.then(({ blob, filename }) => {
			const url = URL.createObjectURL(blob);
			const a = document.createElement("a");
			a.href = url;
			a.download = filename;
			document.body.appendChild(a);
			a.click();
			setTimeout(() => {
				URL.revokeObjectURL(url);
				document.body.removeChild(a);
			}, 500);

			frappe.show_alert({
				message: __("Đã xuất thống kê khách hàng thành công."),
				indicator: "green",
			});
		})
		.catch((err) => {
			console.error("Customer statistics export failed:", err);
		});
}
