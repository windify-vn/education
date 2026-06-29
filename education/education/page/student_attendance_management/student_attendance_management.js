frappe.pages["student-attendance-management"].on_page_load = function (wrapper) {
	if (wrapper.student_attendance_page) {
		wrapper.student_attendance_page.destroy();
	}

	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Quản lý điểm danh"),
		single_column: true,
	});

	wrapper.student_attendance_page = new StudentAttendanceManagementPage(wrapper);
};

frappe.pages["student-attendance-management"].on_page_show = function (wrapper) {
	wrapper.student_attendance_page && wrapper.student_attendance_page.refresh();
};

frappe.pages["student-attendance-management"].on_page_hide = function (wrapper) {
	wrapper.student_attendance_page && wrapper.student_attendance_page.close_transient_state();
};

class StudentAttendanceManagementPage {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.page = wrapper.page;
		this.$wrapper = $(wrapper);
		this.active_tab = "class";
		this.classes = [];
		this.students_by_group = {};
		this.status_options = ["Present", "Absent", "Leave"];
		this.month_date = new Date();
		this.month_date.setDate(1);
		this.month_records = {};
		this.month_original = {};
		this.month_dirty = false;
		this.save_timer = null;
		this.loading = {};
		this.state = {
			class_date: frappe.datetime.get_today(),
			class_group: "",
			report_group: "",
			report_student: "",
			report_mode: "month",
			report_month: this.month_input_value(new Date()),
			report_from: this.month_start(new Date()),
			report_to: this.month_end(new Date()),
			entry_group: "",
			entry_student: "",
		};

		this.make();
		this.load_bootstrap();
	}

	make() {
		this.page.main.empty();
		this.$page = $(`
			<div class="student-attendance-page">
				<div class="student-attendance-tabs">
					<button class="student-attendance-tab is-active" data-tab="class">${__("Điểm danh theo lớp")}</button>
					<button class="student-attendance-tab" data-tab="report">${__("Báo cáo học sinh")}</button>
					
				</div>
				<div class="student-attendance-content"></div>
			</div>
		`).appendTo(this.page.main);
		this.$content = this.$page.find(".student-attendance-content");
		this.bind();
		this.render();
	}

	bind() {
		this.$page.on("click.studentAttendance", "[data-tab]", (event) => {
			this.switch_tab($(event.currentTarget).data("tab"));
		});

		this.$page.on("change.studentAttendance", "[data-field]", (event) => {
			this.handle_field_change(event.currentTarget);
		});

		this.$page.on("click.studentAttendance", "[data-action]", (event) => {
			this.handle_action($(event.currentTarget).data("action"), event.currentTarget);
		});

		this.$page.on("click.studentAttendance", "[data-month-date]", (event) => {
			this.cycle_month_status($(event.currentTarget).data("month-date"));
		});
	}

	load_bootstrap() {
		this.set_loading("bootstrap", true);
		frappe.call({
			method: "education.education.api.get_attendance_status_options",
			callback: (response) => {
				this.status_options = response.message || this.status_options;
				this.load_classes();
			},
			error: () => {
				this.set_error(__("Không thể tải cấu hình trạng thái điểm danh."));
			},
		});
	}

	load_classes() {
		frappe.call({
			method: "education.education.api.get_attendance_classes",
			callback: (response) => {
				this.classes = response.message || [];
				const first = this.classes[0] && this.classes[0].name;
				this.state.class_group = this.state.class_group || first || "";
				this.state.report_group = this.state.report_group || first || "";
				this.state.entry_group = this.state.entry_group || first || "";
				this.set_loading("bootstrap", false);
				this.render();
				["class", "report", "entry"].forEach((scope) => this.load_students_for_scope(scope));
				this.fetch_active_tab();
			},
			error: () => {
				this.set_loading("bootstrap", false);
				this.set_error(__("Không thể tải danh sách lớp."));
			},
		});
	}

	load_students_for_scope(scope, callback) {
		const group = this.state[`${scope}_group`];
		if (!group) {
			callback && callback();
			return;
		}
		if (this.students_by_group[group]) {
			this.ensure_selected_student(scope);
			this.render();
			callback && callback();
			return;
		}
		this.set_loading(`${scope}_students`, true);
		frappe.call({
			method: "education.education.api.get_attendance_students",
			args: { student_group: group },
			callback: (response) => {
				this.students_by_group[group] = response.message || [];
				this.set_loading(`${scope}_students`, false);
				this.ensure_selected_student(scope);
				this.render();
				callback && callback();
			},
			error: () => {
				this.set_loading(`${scope}_students`, false);
				this.set_panel_error(scope, __("Không thể tải danh sách học sinh."));
			},
		});
	}

	ensure_selected_student(scope) {
		if (scope === "class") return;
		const group = this.state[`${scope}_group`];
		const students = this.students_by_group[group] || [];
		const current = this.state[`${scope}_student`];
		if (!students.some((student) => student.student === current)) {
			this.state[`${scope}_student`] = students[0] ? students[0].student : "";
		}
	}

	switch_tab(tab) {
		if (tab === this.active_tab) return;
		const proceed = () => {
			this.active_tab = tab;
			this.$page.find("[data-tab]").removeClass("is-active");
			this.$page.find(`[data-tab="${tab}"]`).addClass("is-active");
			this.render();
			this.fetch_active_tab();
		};
		if (this.month_dirty && this.active_tab === "entry") {
			frappe.confirm(__("Bạn có thay đổi chưa lưu. Tiếp tục chuyển tab?"), () => {
				this.month_dirty = false;
				proceed();
			});
		} else {
			proceed();
		}
	}

	handle_field_change(field) {
		const key = $(field).data("field");
		const value = field.value;
		const apply = () => {
			this.state[key] = value;
			if (key.endsWith("_group")) {
				const scope = key.replace("_group", "");
				this.state[`${scope}_student`] = "";
				this.load_students_for_scope(scope, () => this.fetch_active_tab());
				return;
			}
			if (key === "report_mode") {
				this.render();
			}
			if (key === "entry_student") {
				this.fetch_entry();
				return;
			}
			if (key === "report_student" || key.indexOf("report_") === 0) {
				this.fetch_report();
				return;
			}
			if (key.indexOf("class_") === 0) {
				this.fetch_class();
			}
		};

		if (this.month_dirty && key.indexOf("entry_") === 0) {
			field.value = this.state[key] || "";
			frappe.confirm(__("Bạn có thay đổi chưa lưu. Bỏ thay đổi và tiếp tục?"), () => {
				this.month_dirty = false;
				apply();
			});
		} else {
			apply();
		}
	}

	handle_action(action) {
		if (action === "refresh") {
			this.fetch_active_tab(true);
		} else if (action === "export-class") {
			this.export_table_csv("class");
		} else if (action === "export-report") {
			this.export_table_csv("report");
		} else if (action === "prev-month" || action === "next-month") {
			this.change_entry_month(action === "prev-month" ? -1 : 1);
		} else if (action.indexOf("fill-") === 0) {
			this.quick_fill(action.replace("fill-", ""));
		} else if (action === "clear-month") {
			this.clear_month();
		} else if (action === "save-month") {
			this.save_month();
		}
	}

	fetch_active_tab(force) {
		if (this.active_tab === "class") this.fetch_class(force);
		if (this.active_tab === "report") this.fetch_report(force);
		if (this.active_tab === "entry") this.fetch_entry(force);
	}

	fetch_class() {
		if (!this.state.class_group || !this.state.class_date) {
			this.class_data = null;
			this.render_class();
			return;
		}
		this.set_loading("class", true);
		frappe.call({
			method: "education.education.api.get_class_attendance",
			args: { date: this.state.class_date, student_group: this.state.class_group },
			callback: (response) => {
				this.class_data = response.message;
				this.clear_panel_error("class");
				this.set_loading("class", false);
				this.render_class();
			},
			error: () => {
				this.set_loading("class", false);
				this.set_panel_error("class", __("Không thể tải điểm danh theo lớp."));
			},
		});
	}

	fetch_report() {
		if (!this.state.report_group || !this.state.report_student) {
			this.report_data = null;
			this.render_report();
			return;
		}
		const range = this.get_report_range();
		this.set_loading("report", true);
		frappe.call({
			method: "education.education.api.get_student_attendance_history",
			args: {
				student: this.state.report_student,
				student_group: this.state.report_group,
				from_date: range.from,
				to_date: range.to,
			},
			callback: (response) => {
				this.report_data = response.message;
				this.clear_panel_error("report");
				this.set_loading("report", false);
				this.render_report();
			},
			error: () => {
				this.set_loading("report", false);
				this.set_panel_error("report", __("Không thể tải báo cáo học sinh."));
			},
		});
	}

	fetch_entry() {
		if (!this.state.entry_group || !this.state.entry_student) {
			this.entry_data = null;
			this.month_records = {};
			this.month_original = {};
			this.render_entry();
			return;
		}
		this.set_loading("entry", true);
		frappe.call({
			method: "education.education.api.get_student_month_attendance",
			args: {
				student: this.state.entry_student,
				student_group: this.state.entry_group,
				month: this.month_date.getMonth() + 1,
				year: this.month_date.getFullYear(),
			},
			callback: (response) => {
				this.entry_data = response.message;
				this.month_records = {};
				(response.message.rows || []).forEach((row) => {
					this.month_records[row.date] = row.status;
				});
				this.clear_panel_error("entry");
				if (response.message.holiday_warning) {
					this.set_panel_error("entry", response.message.holiday_warning);
				}
				this.month_original = Object.assign({}, this.month_records);
				this.month_dirty = false;
				this.set_loading("entry", false);
				this.render_entry();
			},
			error: () => {
				this.set_loading("entry", false);
				this.set_panel_error("entry", __("Không thể tải dữ liệu nhập điểm danh."));
			},
		});
	}

	render() {
		if (this.loading.bootstrap) {
			this.$content.html(this.loading_html(__("Đang tải dữ liệu điểm danh...")));
			return;
		}
		if (this.active_tab === "class") this.render_class();
		if (this.active_tab === "report") this.render_report();
		if (this.active_tab === "entry") this.render_entry();
	}

	render_class() {
		const rows = (this.class_data && this.class_data.rows) || [];
		const summary = (this.class_data && this.class_data.summary) || {};
		this.$content.html(`
			<section class="student-attendance-panel" data-panel="class">
				${this.render_class_filters()}
				${this.panel_error_html("class")}
				${this.loading.class ? this.loading_html(__("Đang tải điểm danh theo lớp...")) : this.render_class_body(rows, summary)}
			</section>
		`);
	}

	render_class_filters() {
		return `
			<div class="student-attendance-toolbar">
				${this.render_date("class_date", __("Ngày"), this.state.class_date)}
				${this.render_group_select("class_group", __("Lớp"), this.state.class_group)}
				<div class="student-attendance-actions">
					<button class="attendance-btn" data-action="refresh">${__("Tải lại")}</button>
					<button class="attendance-btn" data-action="export-class" ${this.class_data ? "" : "disabled"}>${__("Xuất báo cáo")}</button>
					<button class="attendance-btn" disabled title="${__("Student Attendance hiện chưa có nghiệp vụ xác nhận riêng.")}">${__("Xác nhận điểm danh")}</button>
				</div>
			</div>
		`;
	}

	render_class_body(rows, summary) {
		if (!this.state.class_group) return this.empty_html(__("Chọn lớp để xem điểm danh."));
		if (!rows.length) return this.empty_html(__("Không có học sinh hoặc dữ liệu điểm danh."));
		return `
			${this.render_stats(summary)}
			<div class="attendance-table-wrap">
				<table class="attendance-table" data-export-table="class">
					<thead><tr><th>${__("STT")}</th><th>${__("Mã học sinh")}</th><th>${__("Họ và tên")}</th><th>${__("Trạng thái")}</th><th>${__("Ghi chú")}</th></tr></thead>
					<tbody>
						${rows
							.map(
								(row, index) => `
								<tr>
									<td>${index + 1}</td>
									<td>${this.escape(row.student)}</td>
									<td>${this.escape(row.student_name)}</td>
									<td>${this.status_badge(row.status)}</td>
									<td>${this.escape(row.note || "")}</td>
								</tr>`
							)
							.join("")}
					</tbody>
				</table>
			</div>
		`;
	}

	render_report() {
		const rows = (this.report_data && this.report_data.rows) || [];
		const summary = (this.report_data && this.report_data.summary) || {};
		const student = (this.report_data && this.report_data.student) || this.get_selected_student("report") || {};
		this.$content.html(`
			<section class="student-attendance-panel" data-panel="report">
				${this.render_report_filters()}
				${this.panel_error_html("report")}
				${this.loading.report ? this.loading_html(__("Đang tải báo cáo học sinh...")) : this.render_report_body(rows, summary, student)}
			</section>
		`);
	}

	render_report_filters() {
		return `
			<div class="student-attendance-toolbar">
				${this.render_group_select("report_group", __("Lớp"), this.state.report_group)}
				${this.render_student_select("report_student", __("Học sinh"), this.state.report_group, this.state.report_student)}
				${this.render_select("report_mode", __("Kiểu xem"), this.state.report_mode, [
					{ value: "month", label: __("Theo tháng") },
					{ value: "range", label: __("Theo khoảng ngày") },
				])}
				${
					this.state.report_mode === "month"
						? this.render_month("report_month", __("Tháng"), this.state.report_month)
						: `${this.render_date("report_from", __("Từ ngày"), this.state.report_from)}${this.render_date(
								"report_to",
								__("Đến ngày"),
								this.state.report_to
						  )}`
				}
				<div class="student-attendance-actions">
					<button class="attendance-btn" data-action="export-report" ${this.report_data ? "" : "disabled"}>${__("Xuất CSV")}</button>
				</div>
			</div>
		`;
	}

	render_report_body(rows, summary, student) {
		if (!this.state.report_student) return this.empty_html(__("Chọn học sinh để xem báo cáo."));
		return `
			<div class="student-report-card">
				<div class="student-avatar">${student.image ? `<img src="${this.escape(student.image)}" alt="">` : this.initials(student.student_name)}</div>
				<div class="student-report-info">
					<div class="student-report-name">${this.escape(student.student_name || student.name || "")}</div>
					<div class="student-report-meta">${this.escape(student.name || student.student || "")} · ${this.escape(this.state.report_group || "")}</div>
					<div class="attendance-progress"><span style="width: ${this.percent(summary.attendance_rate)}%"></span></div>
				</div>
				<div class="student-report-rate">${this.percent(summary.attendance_rate)}%</div>
			</div>
			${this.render_stats(summary)}
			${
				rows.length
					? `<div class="attendance-table-wrap">
						<table class="attendance-table" data-export-table="report">
							<thead><tr><th>${__("STT")}</th><th>${__("Ngày")}</th><th>${__("Thứ")}</th><th>${__("Trạng thái")}</th><th>${__("Ghi chú")}</th></tr></thead>
							<tbody>${rows
								.map(
									(row, index) => `
									<tr>
										<td>${index + 1}</td>
										<td>${this.escape(row.date)}</td>
										<td>${this.weekday(row.date)}</td>
										<td>${this.status_badge(row.status)}</td>
										<td>${this.escape(row.note || "")}</td>
									</tr>`
								)
								.join("")}</tbody>
							<tfoot><tr><td colspan="5">${this.summary_text(summary)}</td></tr></tfoot>
						</table>
					</div>`
					: this.empty_html(__("Không có dữ liệu điểm danh trong khoảng đã chọn."))
			}
		`;
	}

	render_entry() {
		const summary = this.calculate_month_summary();
		this.$content.html(`
			<section class="student-attendance-panel" data-panel="entry">
				${this.render_entry_filters()}
				${this.panel_error_html("entry")}
				${this.loading.entry ? this.loading_html(__("Đang tải tháng điểm danh...")) : this.render_entry_body(summary)}
			</section>
		`);
	}

	render_entry_filters() {
		return `
			<div class="student-attendance-toolbar">
				${this.render_group_select("entry_group", __("Lớp"), this.state.entry_group)}
				${this.render_student_select("entry_student", __("Học sinh"), this.state.entry_group, this.state.entry_student)}
				<div class="month-nav">
					<button class="attendance-icon-btn" data-action="prev-month" aria-label="${__("Tháng trước")}">${this.icon("left", "<")}</button>
					<strong>${this.format_month(this.month_date)}</strong>
					<button class="attendance-icon-btn" data-action="next-month" aria-label="${__("Tháng sau")}">${this.icon("right", ">")}</button>
				</div>
				<div class="student-attendance-actions">
					<span class="dirty-indicator ${this.month_dirty ? "is-dirty" : ""}">${this.month_dirty ? __("Chưa lưu") : __("Đã đồng bộ")}</span>
					<button class="attendance-btn is-primary" data-action="save-month" ${this.month_dirty ? "" : "disabled"}>${__("Lưu điểm danh")}</button>
				</div>
			</div>
		`;
	}

	render_entry_body(summary) {
		if (!this.state.entry_student) return this.empty_html(__("Chọn học sinh để nhập điểm danh."));
		return `
			<div class="entry-layout">
				<div>
					<div class="quick-fill-bar">
						${this.quick_fill_button("Present", __("Set Có mặt"))}
						${this.quick_fill_button("Absent", __("Set Vắng"))}
						${this.quick_fill_button("Late", __("Set Muộn"))}
						${this.quick_fill_button("Leave", __("Set Có phép"))}
						<button class="attendance-btn" data-action="clear-month">${__("Xóa tháng")}</button>
					</div>
					${this.render_month_grid()}
				</div>
				<aside class="entry-side">
					${this.render_entry_summary(summary)}
					<div class="entry-help">
						<div class="entry-help-title">${__("Thứ tự click")}</div>
						<div>${this.cycle_statuses().map((status) => this.status_label(status || "Blank")).join(" → ")}</div>
					</div>
				</aside>
			</div>
		`;
	}

	render_month_grid() {
		const year = this.month_date.getFullYear();
		const month = this.month_date.getMonth();
		const first = new Date(year, month, 1);
		const start = new Date(first);
		start.setDate(first.getDate() - ((first.getDay() + 6) % 7));
		const today = this.date_key(new Date());
		let cells = "";
		for (let index = 0; index < 42; index++) {
			const date = new Date(start);
			date.setDate(start.getDate() + index);
			const key = this.date_key(date);
			const out = date.getMonth() !== month;
			const disabled = out || this.is_non_working_day(date);
			const status = this.month_records[key] || "";
			cells += `
				<button class="month-day ${out ? "is-out" : ""} ${disabled ? "is-weekend" : ""} ${
				key === today ? "is-today" : ""
			}" data-month-date="${key}" ${disabled ? "disabled" : ""}>
					<span>${date.getDate()}</span>
					${status ? `<i class="status-pill status-${this.status_class(status)}">${this.status_label(status)}</i>` : `<i>${__("Chưa đặt")}</i>`}
				</button>`;
		}
		return `
			<div class="month-grid">
				${["T2", "T3", "T4", "T5", "T6", "T7", "CN"].map((day) => `<div class="month-weekday">${day}</div>`).join("")}
				${cells}
			</div>
		`;
	}

	render_entry_summary(summary) {
		return `
			<div class="entry-summary">
				<div class="entry-summary-rate">${this.percent(summary.attendance_rate)}%</div>
				<div class="attendance-progress"><span style="width: ${this.percent(summary.attendance_rate)}%"></span></div>
				${this.summary_row(__("Tổng ngày học"), summary.total)}
				${this.summary_row(__("Đã nhập"), summary.marked)}
				${this.summary_row(__("Có mặt"), summary.present)}
				${this.summary_row(__("Vắng"), summary.absent)}
				${this.summary_row(__("Muộn"), summary.late)}
				${this.summary_row(__("Có phép"), summary.leave)}
				${summary.unmarked ? `<div class="entry-warning">${__("Còn {0} ngày chưa nhập", [summary.unmarked])}</div>` : ""}
				${this.save_message ? `<div class="entry-saved">${this.save_message}</div>` : ""}
			</div>
		`;
	}

	render_stats(summary) {
		return `
			<div class="attendance-stats">
				${this.stat_card(__("Tổng học sinh/ngày"), summary.total || 0)}
				${this.stat_card(__("Có mặt"), summary.present || 0, "Present")}
				${this.stat_card(__("Vắng"), summary.absent || 0, "Absent")}
				${this.stat_card(__("Muộn"), summary.late || 0, "Late")}
				${this.stat_card(__("Có phép"), summary.leave || 0, "Leave")}
			</div>
		`;
	}

	cycle_month_status(key) {
		const date = new Date(key);
		if (date.getMonth() !== this.month_date.getMonth()) return;
		if (this.is_non_working_day(date)) return;
		const statuses = this.cycle_statuses();
		const current = this.month_records[key] || "";
		const next = statuses[(statuses.indexOf(current) + 1) % statuses.length];
		if (next) {
			this.month_records[key] = next;
		} else {
			delete this.month_records[key];
		}
		this.month_dirty = this.is_month_dirty();
		this.render_entry();
	}

	cycle_statuses() {
		return ["Present", "Absent", "Late", "Leave"].filter((status) => status !== "Late" || this.status_options.includes("Late")).concat([""]);
	}

	quick_fill(status) {
		if (!this.status_options.includes(status)) {
			frappe.msgprint(__("Trạng thái {0} chưa tồn tại trong Student Attendance.", [this.status_label(status)]));
			return;
		}
		this.month_working_days().forEach((key) => {
			this.month_records[key] = status;
		});
		this.month_dirty = this.is_month_dirty();
		this.render_entry();
	}

	clear_month() {
		const clear = () => {
			this.month_records = {};
			this.month_dirty = this.is_month_dirty();
			this.render_entry();
		};
		this.month_dirty ? frappe.confirm(__("Xóa toàn bộ trạng thái đang chọn trong tháng?"), clear) : clear();
	}

	save_month() {
		const keys = new Set(this.month_working_days().concat(Object.keys(this.month_original)));
		const records = Array.from(keys).map((date) => ({ date, status: this.month_records[date] || "" }));
		this.set_loading("entry", true);
		frappe.call({
			method: "education.education.api.save_student_month_attendance",
			args: {
				student: this.state.entry_student,
				student_group: this.state.entry_group,
				month: this.month_date.getMonth() + 1,
				year: this.month_date.getFullYear(),
				records: JSON.stringify(records),
			},
			callback: () => {
				this.save_message = __("Đã lưu!");
				frappe.show_alert({ message: __("Đã lưu điểm danh"), indicator: "green" });
				this.fetch_entry();
				clearTimeout(this.save_timer);
				this.save_timer = setTimeout(() => {
					this.save_message = "";
					this.render_entry();
				}, 2000);
			},
			error: () => {
				this.set_loading("entry", false);
				this.set_panel_error("entry", __("Không thể lưu điểm danh tháng."));
			},
		});
	}

	change_entry_month(delta) {
		const change = () => {
			this.month_date.setMonth(this.month_date.getMonth() + delta);
			this.month_date.setDate(1);
			this.month_dirty = false;
			this.fetch_entry();
		};
		this.month_dirty ? frappe.confirm(__("Bạn có thay đổi chưa lưu. Bỏ thay đổi và đổi tháng?"), change) : change();
	}

	calculate_month_summary() {
		const rows = this.month_working_days().map((date) => ({ status: this.month_records[date] || "" }));
		const summary = { total: rows.length, marked: 0, present: 0, absent: 0, late: 0, leave: 0, unmarked: 0 };
		rows.forEach((row) => {
			if (!row.status) {
				summary.unmarked++;
			} else {
				summary.marked++;
				if (row.status === "Present") summary.present++;
				if (row.status === "Absent") summary.absent++;
				if (row.status === "Late") summary.late++;
				if (row.status === "Leave") summary.leave++;
			}
		});
		summary.attendance_rate = summary.marked ? (summary.present / summary.marked) * 100 : 0;
		return summary;
	}

	month_working_days() {
		const days = [];
		const date = new Date(this.month_date);
		while (date.getMonth() === this.month_date.getMonth()) {
			if (!this.is_non_working_day(date)) {
				days.push(this.date_key(date));
			}
			date.setDate(date.getDate() + 1);
		}
		return days;
	}

	is_non_working_day(date) {
		const key = this.date_key(date);
		const holidays = (this.entry_data && this.entry_data.non_working_dates) || [];
		if (holidays.length) {
			return holidays.includes(key);
		}
		return date.getDay() === 0 || date.getDay() === 6;
	}

	is_month_dirty() {
		const keys = new Set(Object.keys(this.month_records).concat(Object.keys(this.month_original)));
		for (const key of keys) {
			if ((this.month_records[key] || "") !== (this.month_original[key] || "")) return true;
		}
		return false;
	}

	export_table_csv(type) {
		const table = this.$page.find(`[data-export-table="${type}"]`)[0];
		if (!table) return;
		const rows = Array.from(table.querySelectorAll("tr")).map((tr) =>
			Array.from(tr.children).map((cell) => `"${cell.innerText.replace(/"/g, '""')}"`).join(",")
		);
		const blob = new Blob(["\ufeff" + rows.join("\n")], { type: "text/csv;charset=utf-8;" });
		const url = URL.createObjectURL(blob);
		const link = document.createElement("a");
		link.href = url;
		link.download = `${type}-attendance-${frappe.datetime.get_today()}.csv`;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		URL.revokeObjectURL(url);
	}

	get_report_range() {
		if (this.state.report_mode === "month") {
			const parts = (this.state.report_month || this.month_input_value(new Date())).split("-");
			const year = parseInt(parts[0], 10);
			const month = parseInt(parts[1], 10);
			const last = new Date(year, month, 0).getDate();
			return { from: `${year}-${String(month).padStart(2, "0")}-01`, to: `${year}-${String(month).padStart(2, "0")}-${last}` };
		}
		return { from: this.state.report_from, to: this.state.report_to };
	}

	render_group_select(field, label, value) {
		return this.render_select(
			field,
			label,
			value,
			this.classes.map((group) => ({
				value: group.name,
				label: [group.student_group_name || group.name, group.program].filter(Boolean).join(" · "),
			}))
		);
	}

	render_student_select(field, label, group, value) {
		const students = this.students_by_group[group] || [];
		return this.render_select(
			field,
			label,
			value,
			students.map((student) => ({ value: student.student, label: `${student.student_name || student.student} (${student.student})` })),
			this.loading[`${field.replace("_student", "")}_students`] ? __("Đang tải...") : __("Chọn học sinh")
		);
	}

	render_select(field, label, value, options, placeholder) {
		return `
			<label class="attendance-field">
				<span>${label}</span>
				<select data-field="${field}">
					<option value="">${placeholder || __("Chọn")}</option>
					${(options || [])
						.map((option) => `<option value="${this.escape(option.value)}" ${option.value === value ? "selected" : ""}>${this.escape(option.label)}</option>`)
						.join("")}
				</select>
			</label>
		`;
	}

	render_date(field, label, value) {
		return `<label class="attendance-field"><span>${label}</span><input type="date" data-field="${field}" value="${this.escape(value || "")}" /></label>`;
	}

	render_month(field, label, value) {
		return `<label class="attendance-field"><span>${label}</span><input type="month" data-field="${field}" value="${this.escape(value || "")}" /></label>`;
	}

	stat_card(label, value, status) {
		return `<div class="attendance-stat ${status ? `status-border-${this.status_class(status)}` : ""}"><span>${label}</span><strong>${value}</strong></div>`;
	}

	summary_row(label, value) {
		return `<div class="summary-row"><span>${label}</span><strong>${value || 0}</strong></div>`;
	}

	status_badge(status) {
		return status
			? `<span class="status-pill status-${this.status_class(status)}">${this.status_label(status)}</span>`
			: `<span class="status-pill status-empty">${__("Chưa đặt")}</span>`;
	}

	quick_fill_button(status, label) {
		return `<button class="attendance-btn" data-action="fill-${status}" ${this.status_options.includes(status) ? "" : "disabled"}>${label}</button>`;
	}

	status_label(status) {
		const labels = { Present: __("Có mặt"), Absent: __("Vắng"), Late: __("Muộn"), Leave: __("Có phép"), Blank: __("Chưa đặt") };
		return labels[status] || status || __("Chưa đặt");
	}

	status_class(status) {
		return String(status || "empty").toLowerCase().replace(/[^a-z0-9]+/g, "-");
	}

	get_selected_student(scope) {
		const students = this.students_by_group[this.state[`${scope}_group`]] || [];
		return students.find((student) => student.student === this.state[`${scope}_student`]);
	}

	summary_text(summary) {
		return __("Tổng: {0} · Có mặt: {1} · Vắng: {2} · Muộn: {3} · Có phép: {4} · Tỷ lệ: {5}%", [
			summary.total || 0,
			summary.present || 0,
			summary.absent || 0,
			summary.late || 0,
			summary.leave || 0,
			this.percent(summary.attendance_rate),
		]);
	}

	set_loading(key, value) {
		this.loading[key] = value;
	}

	set_panel_error(scope, message) {
		this.errors = this.errors || {};
		this.errors[scope] = message;
		this.render();
	}

	clear_panel_error(scope) {
		this.errors = this.errors || {};
		delete this.errors[scope];
	}

	set_error(message) {
		this.$content.html(`<div class="attendance-error">${this.escape(message)}</div>`);
	}

	panel_error_html(scope) {
		const message = this.errors && this.errors[scope];
		return message ? `<div class="attendance-error">${this.escape(message)}</div>` : "";
	}

	loading_html(message) {
		return `<div class="attendance-loading">${this.escape(message)}</div>`;
	}

	empty_html(message) {
		return `<div class="attendance-empty">${this.escape(message)}</div>`;
	}

	icon(name, fallback) {
		return frappe.utils && frappe.utils.icon ? frappe.utils.icon(name, "sm") : `<span>${fallback || ""}</span>`;
	}

	escape(value) {
		return frappe.utils.escape_html(value == null ? "" : String(value));
	}

	initials(value) {
		return this.escape(
			String(value || "?")
				.split(" ")
				.map((part) => part[0])
				.slice(0, 2)
				.join("")
				.toUpperCase()
		);
	}

	percent(value) {
		return Math.max(0, Math.min(100, Number(value || 0))).toFixed(0);
	}

	weekday(date) {
		return new Intl.DateTimeFormat(frappe.boot.lang || undefined, { weekday: "short" }).format(new Date(date));
	}

	format_month(date) {
		return new Intl.DateTimeFormat(frappe.boot.lang || undefined, { month: "long", year: "numeric" }).format(date);
	}

	month_input_value(date) {
		return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
	}

	month_start(date) {
		return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-01`;
	}

	month_end(date) {
		return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(
			new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate()
		).padStart(2, "0")}`;
	}

	date_key(date) {
		return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
	}

	close_transient_state() {
		clearTimeout(this.save_timer);
	}

	refresh() {
		this.fetch_active_tab();
	}

	destroy() {
		this.close_transient_state();
		this.$page && this.$page.off(".studentAttendance");
	}
}
