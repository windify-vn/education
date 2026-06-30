const SCHOOL_CALENDAR_FALLBACK_LANGUAGE = "vi";
const SCHOOL_CALENDAR_SUPPORTED_LANGUAGES = new Set(["en", "vi"]);
const SCHOOL_CALENDAR_VI_MESSAGES = {
	"4 days": "4 ngày",
	"Academy Calendar": "Lịch học viện",
	"All day": "Cả ngày",
	Amber: "Hổ phách",
	Apply: "Áp dụng",
	Assistant: "Trợ giảng",
	Blue: "Xanh dương",
	Calendar: "Lịch",
	"Calendar library is not available.": "Không tải được thư viện lịch.",
	"Calendar settings": "Cài đặt lịch",
	Cancelled: "Đã hủy",
	Cyan: "Xanh lơ",
	"Clear resource filters": "Xóa bộ lọc nguồn lực",
	Closed: "Đã đóng",
	Color: "Màu",
	"Compact event rows": "Thu gọn dòng sự kiện",
	Completed: "Hoàn thành",
	Continue: "Tiếp tục",
	Course: "Khóa học",
	"Course Schedule": "Lịch dạy",
	"Course Schedule created": "Đã tạo lịch dạy",
	"Course Schedule must start and end on the same date": "Lịch dạy phải bắt đầu và kết thúc trong cùng một ngày",
	"Create": "Tạo mới",
	"Create Course Schedule": "Tạo lịch dạy",
	"Create event": "Tạo sự kiện",
	Day: "Ngày",
	Delete: "Xóa",
	"Delete this event?": "Xóa sự kiện này?",
	"Delete this schedule?": "Xóa lịch dạy này?",
	Description: "Mô tả",
	Edit: "Chỉnh sửa",
	"Edit event": "Chỉnh sửa sự kiện",
	"End date must be after start date": "Thời gian kết thúc phải sau thời gian bắt đầu",
	"Ends on": "Kết thúc",
	Event: "Sự kiện",
	"Event deleted": "Đã xóa sự kiện",
	"Event saved": "Đã lưu sự kiện",
	"Future Academy": "Future Academy",
	Green: "Xanh lá",
	Instructor: "Giảng viên",
	Loading: "Đang tải",
	Menu: "Menu",
	"Missing calendar date range": "Thiếu khoảng thời gian của lịch",
	Month: "Tháng",
	"My Events": "Sự kiện của tôi",
	"Next month": "Tháng sau",
	Next: "Tiếp",
	"No assistants in this range": "Không có trợ giảng trong khoảng này",
	"No events to display": "Không có sự kiện để hiển thị",
	"No instructors in this range": "Không có giảng viên trong khoảng này",
	"No people found": "Không tìm thấy người phù hợp",
	"Not permitted": "Không có quyền",
	"Not permitted to create course schedules": "Không có quyền tạo lịch dạy",
	"Not permitted to create events": "Không có quyền tạo sự kiện",
	"Not permitted to delete this course schedule": "Không có quyền xóa lịch dạy này",
	"Not permitted to delete this event": "Không có quyền xóa sự kiện này",
	"Not permitted to read this event": "Không có quyền xem sự kiện này",
	"Not permitted to update this event": "Không có quyền cập nhật sự kiện này",
	Open: "Mở",
	Orange: "Cam",
	Pink: "Hồng",
	Previous: "Trước",
	"Previous month": "Tháng trước",
	Private: "Riêng tư",
	Public: "Công khai",
	Purple: "Tím",
	Red: "Đỏ",
	Resource: "Nguồn lực",
	Room: "Phòng",
	Save: "Lưu",
	Schedule: "Lịch biểu",
	"Schedule deleted": "Đã xóa lịch dạy",
	Search: "Tìm kiếm",
	"Search for people": "Tìm người",
	Settings: "Cài đặt",
	"Show weekends": "Hiển thị cuối tuần",
	"Starts on": "Bắt đầu",
	Status: "Trạng thái",
	"Student Group": "Lớp học",
	Teal: "Xanh ngọc",
	"This calendar record cannot be deleted": "Không thể xóa bản ghi lịch này",
	"This calendar view is not available.": "Chế độ xem lịch này không khả dụng.",
	Title: "Tiêu đề",
	"Title is required": "Tiêu đề là bắt buộc",
	Today: "Hôm nay",
	"Toggle sidebar": "Ẩn hiện thanh bên",
	"Untitled Event": "Sự kiện chưa có tiêu đề",
	Violet: "Tím violet",
	Visibility: "Hiển thị",
	Week: "Tuần",
	Year: "Năm",
	Yellow: "Vàng",
	"You do not have permission to create calendar records.": "Bạn không có quyền tạo bản ghi lịch.",
	"You do not have permission to create this calendar record.": "Bạn không có quyền tạo bản ghi lịch này.",
	"{0} is required": "{0} là bắt buộc",
	events: "sự kiện",
};
const SCHOOL_CALENDAR_VI_FULLCALENDAR_LOCALE = {
	code: "vi",
	week: {
		dow: 1,
		doy: 4,
	},
	buttonText: {
		prev: "Trước",
		next: "Tiếp",
		today: "Hôm nay",
		year: "Năm",
		month: "Tháng",
		week: "Tuần",
		day: "Ngày",
		list: "Lịch biểu",
	},
	weekText: "Tu",
	allDayText: "Cả ngày",
	moreLinkText(count) {
		return `+ thêm ${count}`;
	},
	noEventsText: "Không có sự kiện để hiển thị",
};

function school_calendar_user_language_base() {
	const language = (frappe.boot && (frappe.boot.lang || frappe.boot.user_language)) || SCHOOL_CALENDAR_FALLBACK_LANGUAGE;
	return String(language).replace("_", "-").toLowerCase().split("-")[0];
}

function school_calendar_effective_language() {
	const language = school_calendar_user_language_base();
	return SCHOOL_CALENDAR_SUPPORTED_LANGUAGES.has(language) ? language : SCHOOL_CALENDAR_FALLBACK_LANGUAGE;
}

function school_calendar_t(message) {
	const key = String(message || "");
	const language = school_calendar_effective_language();

	if (language === "en") {
		return __(key);
	}

	if (school_calendar_user_language_base() === "vi") {
		const translated = __(key);
		if (translated && translated !== key) {
			return translated;
		}
	}

	return SCHOOL_CALENDAR_VI_MESSAGES[key] || key;
}

frappe.pages["school-calendar"].on_page_load = function (wrapper) {
	if (wrapper.school_calendar_page) {
		wrapper.school_calendar_page.destroy();
	}

	frappe.ui.make_app_page({
		parent: wrapper,
		title: school_calendar_t("Future Academy"),
		single_column: true,
	});

	wrapper.school_calendar_page = new SchoolCalendarPage(wrapper);
};

frappe.pages["school-calendar"].on_page_show = function (wrapper) {
	if (wrapper.school_calendar_page) {
		wrapper.school_calendar_page.refresh();
	}
};

frappe.pages["school-calendar"].on_page_hide = function (wrapper) {
	if (wrapper.school_calendar_page) {
		wrapper.school_calendar_page.close_popover();
	}
};

class SchoolCalendarPage {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.$wrapper = $(wrapper);
		this.page = wrapper.page;
		this.current_date = new Date();
		this.current_view = "month";
		this.sources = [];
		this.enabled_sources = new Set();
		this.saved_enabled_sources = null;
		this.resource_filters = new Set();
		this.saved_resource_filters = null;
		this.resource_people = {
			instructor: [],
			teaching_assistant: [],
		};
		this.active_resource_tab = "instructor";
		this.resource_search_text = "";
		this.has_saved_view = false;
		this.search_text = "";
		this.search_timer = null;
		this.people_timer = null;
		this.calendar = null;
		this.mobile_breakpoint = 720;
		this.year_events = [];
		this.storage_key = "education_school_calendar_state_v1";
		this.settings = {
			weekends: true,
			compact_events: false,
			sidebar_collapsed: false,
		};

		this.view_map = {
			day: "timeGridDay",
			week: "timeGridWeek",
			month: "dayGridMonth",
			year: "dayGridMonth",
			schedule: "listWeek",
			four_days: "fourDay",
		};
		this.load_local_state();
		this.make();
		this.load();
	}

	make() {
		this.page.main.empty();
		this.$page = $(`
			<div class="school-calendar-page">
				<div class="school-calendar-topbar">
					<div class="school-calendar-topbar-left">
						<button class="school-icon-btn" data-action="toggle-sidebar" aria-label="${this.t("Toggle sidebar")}"></button>
						<div class="school-calendar-title">${this.t("Calendar")}</div>
						<button class="school-text-btn" data-action="today">${this.t("Today")}</button>
						<div class="school-nav-group">
							<button class="school-icon-btn" data-action="prev" aria-label="${this.t("Previous")}"></button>
							<button class="school-icon-btn" data-action="next" aria-label="${this.t("Next")}"></button>
						</div>
						<div class="school-calendar-range-label"></div>
					</div>
					<div class="school-calendar-topbar-right">
						<div class="school-search">
							<span class="school-search-icon"></span>
							<input type="search" data-field="search" placeholder="${this.t("Search")}" />
						</div>
						<button class="school-icon-btn" data-action="settings" aria-label="${this.t("Settings")}"></button>
						<select class="school-view-select" data-field="view">
							<option value="day">${this.t("Day")}</option>
							<option value="week">${this.t("Week")}</option>
							<option value="month" selected>${this.t("Month")}</option>
							<option value="year">${this.t("Year")}</option>
							<option value="schedule">${this.t("Schedule")}</option>
							<option value="four_days">${this.t("4 days")}</option>
						</select>
					</div>
				</div>
				<div class="school-calendar-shell">
					<aside class="school-calendar-sidebar">
						<button class="school-create-btn" data-action="create">
							<span class="school-create-plus">+</span>
							<span>${this.t("Create")}</span>
						</button>
						<div class="school-mini-calendar">
							<div class="school-mini-head">
								<button class="school-icon-btn school-mini-prev" data-action="mini-prev" aria-label="${this.t("Previous month")}"></button>
								<div class="school-mini-title"></div>
								<button class="school-icon-btn school-mini-next" data-action="mini-next" aria-label="${this.t("Next month")}"></button>
							</div>
							<div class="school-mini-weekdays"></div>
							<div class="school-mini-grid"></div>
						</div>
						<div class="school-sidebar-section">
							<button class="school-section-toggle" data-section="resources">
								<span>${this.t("Resource")}</span>
								<span class="school-section-caret"></span>
							</button>
							<div class="school-resource-panel">
								<label class="school-sidebar-label">${this.t("Search for people")}</label>
								<div class="school-resource-search">
									<span class="school-resource-search-icon"></span>
									<input class="school-people-input" type="search" data-field="people" placeholder="${this.t("Search for people")}" />
								</div>
								<div class="school-resource-tabs">
									<button class="school-resource-tab is-active" type="button" data-resource-tab="instructor">${this.t("Instructor")}</button>
									<button class="school-resource-tab" type="button" data-resource-tab="teaching_assistant">${this.t("Assistant")}</button>
								</div>
								<div class="school-source-list" data-resource-list="resources"></div>
							</div>
						</div>
					</aside>
					<main class="school-calendar-main">
						<div class="school-calendar-node"></div>
						<div class="school-year-node is-hidden"></div>
					</main>
				</div>
			</div>
		`).appendTo(this.page.main);

		this.$calendar_node = this.$page.find(".school-calendar-node");
		this.$year_node = this.$page.find(".school-year-node");
		this.$page.find('[data-field="view"]').val(this.current_view);
		this.apply_settings_classes();
		this.set_icons();
		this.bind();
		this.render_mini_calendar();
	}

	icon(name, fallback) {
		return frappe.utils && frappe.utils.icon ? frappe.utils.icon(name, "sm") : `<span>${fallback || ""}</span>`;
	}

	escape(value) {
		return frappe.utils.escape_html(value || "");
	}

	t(message) {
		return school_calendar_t(message);
	}

	get_effective_language() {
		return school_calendar_effective_language();
	}

	get_calendar_locale() {
		return this.get_effective_language() === "en" ? "en" : SCHOOL_CALENDAR_FALLBACK_LANGUAGE;
	}

	get_date_locale() {
		return this.get_calendar_locale() === "en" ? "en" : "vi-VN";
	}

	get_weekday_labels() {
		if (this.get_calendar_locale() === "vi") {
			return ["T2", "T3", "T4", "T5", "T6", "T7", "CN"];
		}
		return ["M", "T", "W", "T", "F", "S", "S"];
	}

	get_color_options() {
		return [
			{ value: "blue", label: this.t("Blue") },
			{ value: "green", label: this.t("Green") },
			{ value: "red", label: this.t("Red") },
			{ value: "orange", label: this.t("Orange") },
			{ value: "yellow", label: this.t("Yellow") },
			{ value: "teal", label: this.t("Teal") },
			{ value: "violet", label: this.t("Violet") },
			{ value: "cyan", label: this.t("Cyan") },
			{ value: "amber", label: this.t("Amber") },
			{ value: "pink", label: this.t("Pink") },
			{ value: "purple", label: this.t("Purple") },
		];
	}

	get_visibility_options() {
		return [
			{ value: "Private", label: this.t("Private") },
			{ value: "Public", label: this.t("Public") },
		];
	}

	get_status_options() {
		return [
			{ value: "Open", label: this.t("Open") },
			{ value: "Completed", label: this.t("Completed") },
			{ value: "Closed", label: this.t("Closed") },
			{ value: "Cancelled", label: this.t("Cancelled") },
		];
	}

	set_icons() {
		this.$page.find('[data-action="toggle-sidebar"]').html(this.icon("menu", this.t("Menu")));
		this.$page.find('[data-action="prev"]').html(this.icon("left", "<"));
		this.$page.find('[data-action="next"]').html(this.icon("right", ">"));
		this.$page.find('[data-action="mini-prev"]').html(this.icon("left", "<"));
		this.$page.find('[data-action="mini-next"]').html(this.icon("right", ">"));
		this.$page.find('[data-action="settings"]').html(this.icon("setting-gear", this.t("Settings")));
		this.$page.find(".school-search-icon").html(this.icon("search", this.t("Search")));
		this.$page.find(".school-resource-search-icon").html(this.icon("search", this.t("Search")));
		this.$page.find(".school-section-caret").html(this.icon("down", "v"));
	}

	load_local_state() {
		try {
			const state = JSON.parse(window.localStorage.getItem(this.storage_key) || "{}");
			if (state && this.view_map[state.view]) {
				this.current_view = state.view;
				this.has_saved_view = true;
			}
			if (Array.isArray(state.enabled_sources)) {
				this.saved_enabled_sources = state.enabled_sources;
			}
			if (Array.isArray(state.resource_filters)) {
				this.saved_resource_filters = state.resource_filters.filter((resource) => resource.includes("::"));
			}
			this.settings = Object.assign({}, this.settings, state.settings || {});
		} catch (error) {
			console.warn("Could not load school calendar state", error);
		}
	}

	save_local_state() {
		try {
			window.localStorage.setItem(
				this.storage_key,
				JSON.stringify({
					view: this.current_view,
					enabled_sources: Array.from(this.enabled_sources),
					resource_filters: Array.from(this.resource_filters),
					settings: this.settings,
				})
			);
		} catch (error) {
			console.warn("Could not save school calendar state", error);
		}
	}

	apply_settings_classes() {
		if (!this.$page) return;
		this.$page.toggleClass("is-sidebar-collapsed", Boolean(this.settings.sidebar_collapsed));
		this.$page.toggleClass("is-compact-events", Boolean(this.settings.compact_events));
	}

	bind() {
		this.$page.on("click.schoolCalendar", "[data-action]", (event) => {
			const action = $(event.currentTarget).data("action");
			this.handle_action(action, event.currentTarget);
		});

		this.$page.on("change.schoolCalendar", '[data-field="view"]', (event) => {
			this.change_view(event.currentTarget.value);
		});

		this.$page.on("input.schoolCalendar", '[data-field="search"]', (event) => {
			clearTimeout(this.search_timer);
			this.search_timer = setTimeout(() => {
				this.search_text = event.currentTarget.value || "";
				this.refetch_events();
			}, 250);
		});

		this.$page.on("input.schoolCalendar", '[data-field="people"]', (event) => {
			clearTimeout(this.people_timer);
			this.people_timer = setTimeout(() => {
				this.resource_search_text = event.currentTarget.value || "";
				this.render_resource_filters();
			}, 250);
		});

		this.$page.on("change.schoolCalendar", "[data-source]", (event) => {
			const source = event.currentTarget.value;
			if (event.currentTarget.checked) {
				this.enabled_sources.add(source);
			} else {
				this.enabled_sources.delete(source);
			}
			this.save_local_state();
			this.load_current_resources();
			this.refetch_events();
		});

		this.$page.on("change.schoolCalendar", "[data-resource]", (event) => {
			const resource = event.currentTarget.value;
			if (event.currentTarget.checked) {
				this.resource_filters.add(resource);
			} else {
				this.resource_filters.delete(resource);
			}
			this.save_local_state();
			this.refetch_events();
		});

		this.$page.on("click.schoolCalendar", "[data-resource-tab]", (event) => {
			this.active_resource_tab = $(event.currentTarget).data("resource-tab");
			this.render_resource_filters();
		});

		this.$page.on("click.schoolCalendar", "[data-action='clear-resource-filters']", () => {
			this.resource_filters.clear();
			this.save_local_state();
			this.render_resource_filters();
			this.refetch_events();
		});

		this.$page.on("click.schoolCalendar", "[data-mini-date]", (event) => {
			const date = new Date($(event.currentTarget).data("mini-date"));
			this.go_to_date(date);
		});

		this.$page.on("click.schoolCalendar", "[data-year-date]", (event) => {
			const date = new Date($(event.currentTarget).data("year-date"));
			this.go_to_date(date);
			this.$page.find('[data-field="view"]').val("day");
			this.change_view("day");
		});

		this.$page.on("click.schoolCalendar", "[data-year-month]", (event) => {
			const date = new Date($(event.currentTarget).data("year-month"));
			this.go_to_date(date);
			this.$page.find('[data-field="view"]').val("month");
			this.change_view("month");
		});

		this.$page.on("click.schoolCalendar", ".school-section-toggle", (event) => {
			$(event.currentTarget).toggleClass("is-collapsed");
			$(event.currentTarget).next().toggleClass("is-hidden");
		});

		$(document).on("keydown.schoolCalendar", (event) => {
			if ($(event.target).is("input, textarea, select")) return;
			if (event.key === "t") {
				this.go_today();
			}
		});

		$(document).on("click.schoolCalendar", (event) => {
			if (!$(event.target).closest(".school-event-popover, .fc-event").length) {
				this.close_popover();
			}
		});
	}

	handle_action(action) {
		if (action === "toggle-sidebar") {
			this.settings.sidebar_collapsed = !this.settings.sidebar_collapsed;
			this.apply_settings_classes();
			this.save_local_state();
		} else if (action === "today") {
			this.go_today();
		} else if (action === "prev") {
			if (this.is_year_view()) {
				this.current_date.setFullYear(this.current_date.getFullYear() - 1);
				this.render_year_view();
			} else {
				this.calendar && this.calendar.prev();
				this.sync_from_calendar();
			}
		} else if (action === "next") {
			if (this.is_year_view()) {
				this.current_date.setFullYear(this.current_date.getFullYear() + 1);
				this.render_year_view();
			} else {
				this.calendar && this.calendar.next();
				this.sync_from_calendar();
			}
		} else if (action === "mini-prev") {
			this.current_date = this.add_months(this.current_date, -1);
			this.render_mini_calendar();
		} else if (action === "mini-next") {
			this.current_date = this.add_months(this.current_date, 1);
			this.render_mini_calendar();
		} else if (action === "create") {
			this.open_create_dialog();
		} else if (action === "settings") {
			this.open_settings_dialog();
		}
	}

	load() {
		frappe.require("calendar.bundle.js", () => {
			frappe.call({
				method: "education.education.api.get_calendar_sources",
				callback: (response) => {
					this.sources = response.message || [];
					this.enabled_sources = new Set(this.sources.filter((source) => source.checked).map((source) => source.id));
					if (this.saved_resource_filters) {
						this.resource_filters = new Set(this.saved_resource_filters);
					}
					this.render_resource_filters();
					this.update_create_button_state();
					this.make_calendar();
				},
			});
		});
	}

	make_calendar() {
		if (!frappe.FullCalendar) {
			frappe.msgprint(this.t("Calendar library is not available."));
			return;
		}

		this.calendar = new frappe.FullCalendar(this.$calendar_node[0], {
			plugins: frappe.FullCalendar.Plugins,
			locales: [SCHOOL_CALENDAR_VI_FULLCALENDAR_LOCALE],
			initialDate: this.current_date,
			initialView: this.get_initial_view(),
			headerToolbar: false,
			height: "100%",
			locale: this.get_calendar_locale(),
			firstDay: 1,
			weekends: Boolean(this.settings.weekends),
			nowIndicator: true,
			selectable: false,
			editable: true,
			eventResizableFromStart: true,
			dayMaxEvents: 3,
			allDaySlot: true,
			slotMinTime: "00:00:00",
			slotMaxTime: "24:00:00",
			views: {
				fourDay: {
					type: "timeGrid",
					duration: { days: 4 },
				},
			},
			events: (info, success, failure) => {
				frappe.call({
					method: "education.education.api.get_calendar_events",
					type: "GET",
					args: {
						start: this.to_system_datetime(info.start),
						end: this.to_system_datetime(info.end),
						calendars: JSON.stringify(Array.from(this.enabled_sources)),
						resource_filters: JSON.stringify(Array.from(this.resource_filters)),
						search: this.search_text,
						view: this.current_view,
					},
					callback: (response) => success(response.message || []),
					error: failure,
				});
			},
			eventContent: (info) => this.render_event_content(info),
			eventDidMount: (info) => {
				const props = info.event.extendedProps || {};
				info.el.setAttribute("title", [info.event.title, props.subtitle].filter(Boolean).join("\n"));
			},
			moreLinkClick: "popover",
			datesSet: () => {
				this.sync_from_calendar();
				this.load_current_resources();
			},
			eventClick: (info) => {
				info.jsEvent.preventDefault();
				this.open_event_popover(info.event, info.el);
			},
			eventDrop: (info) => this.persist_event_move(info),
			eventResize: (info) => this.persist_event_move(info),
		});

		this.calendar.render();
		this.update_range_label();
	}

	is_year_view() {
		return this.current_view === "year";
	}

	get_initial_view() {
		if (window.innerWidth <= this.mobile_breakpoint && !this.has_saved_view) {
			this.current_view = "schedule";
			this.$page.find('[data-field="view"]').val("schedule");
		}
		return this.view_map[this.current_view];
	}

	render_event_content(info) {
		const props = info.event.extendedProps || {};
		const subtitle = props.subtitle || "";
		const title = this.escape(info.event.title);
		const subtitle_html = subtitle ? `<div class="school-fc-event-subtitle">${this.escape(subtitle)}</div>` : "";
		return { html: `<div class="school-fc-event-title">${title}</div>${subtitle_html}` };
	}

	render_resource_filters() {
		const $list = this.$page.find('[data-resource-list="resources"]').empty();
		this.$page.find("[data-resource-tab]").removeClass("is-active");
		this.$page.find(`[data-resource-tab="${this.active_resource_tab}"]`).addClass("is-active");

		const resources = this.get_visible_resources();
		if (this.resource_filters.size) {
			$(`
				<button class="school-clear-resource-filters" type="button" data-action="clear-resource-filters">
					${this.t("Clear resource filters")}
				</button>
			`).appendTo($list);
		}

		if (!resources.length) {
			const empty_message = this.resource_search_text.trim()
				? this.t("No people found")
				: this.active_resource_tab === "instructor"
				? this.t("No instructors in this range")
				: this.t("No assistants in this range");
			$(`<div class="school-muted-block">${this.escape(empty_message)}</div>`).appendTo($list);
			return;
		}

		resources.forEach((resource) => {
			$(`
				<label class="school-source-row school-resource-row">
					<input type="checkbox" data-resource="${this.escape(resource.id)}" value="${this.escape(resource.id)}" ${
				this.resource_filters.has(resource.id) ? "checked" : ""
			} />
					<span class="school-source-dot" style="--source-color: ${this.escape(resource.color)}"></span>
					<span class="school-source-label">
						<span>${this.escape(resource.label)}</span>
						<small>${this.escape(resource.name)} · ${this.escape(resource.count)} ${this.t("events")}</small>
					</span>
				</label>
			`).appendTo($list);
		});
	}

	get_visible_resources() {
		const search = this.resource_search_text.trim().toLowerCase();
		return (this.resource_people[this.active_resource_tab] || []).filter((resource) => {
			if (!search) return true;
			return [resource.label, resource.name].some((value) => String(value || "").toLowerCase().includes(search));
		});
	}

	load_current_resources() {
		if (this.is_year_view()) {
			const year = this.current_date.getFullYear();
			this.load_calendar_resources(new Date(year, 0, 1), new Date(year + 1, 0, 1));
			return;
		}
		if (!this.calendar || !this.calendar.view) return;
		this.load_calendar_resources(this.calendar.view.activeStart, this.calendar.view.activeEnd);
	}

	load_calendar_resources(start, end) {
		if (!start || !end) return;
		frappe.call({
			method: "education.education.api.get_calendar_resources",
			type: "GET",
			args: {
				start: this.to_system_datetime(start),
				end: this.to_system_datetime(end),
				calendars: JSON.stringify(Array.from(this.enabled_sources)),
			},
			callback: (response) => {
				this.resource_people = Object.assign(
					{ instructor: [], teaching_assistant: [] },
					response.message || {}
				);
				this.render_resource_filters();
			},
		});
	}

	render_mini_calendar() {
		const date = new Date(this.current_date);
		const year = date.getFullYear();
		const month = date.getMonth();
		const first = new Date(year, month, 1);
		const today_key = this.date_key(new Date());
		const selected_key = this.date_key(this.current_date);
		const start = new Date(first);
		const monday_offset = (first.getDay() + 6) % 7;
		start.setDate(first.getDate() - monday_offset);

		this.$page.find(".school-mini-title").text(this.format_month_year(date));
		this.$page
			.find(".school-mini-weekdays")
			.html(this.get_weekday_labels().map((day) => `<span>${day}</span>`).join(""));

		let html = "";
		for (let index = 0; index < 42; index++) {
			const cell = new Date(start);
			cell.setDate(start.getDate() + index);
			const key = this.date_key(cell);
			const classes = [
				"school-mini-day",
				cell.getMonth() !== month ? "is-muted" : "",
				key === today_key ? "is-today" : "",
				key === selected_key ? "is-selected" : "",
			]
				.filter(Boolean)
				.join(" ");
			html += `<button class="${classes}" data-mini-date="${key}">${cell.getDate()}</button>`;
		}
		this.$page.find(".school-mini-grid").html(html);
	}

	change_view(view) {
		this.current_view = view;
		this.save_local_state();
		if (this.is_year_view()) {
			this.$calendar_node.addClass("is-hidden");
			this.$year_node.removeClass("is-hidden");
			this.render_year_view();
			return;
		}

		this.$year_node.addClass("is-hidden");
		this.$calendar_node.removeClass("is-hidden");
		if (this.calendar) {
			try {
				this.calendar.changeView(this.view_map[view], this.current_date);
			} catch (error) {
				console.error(error);
				this.current_view = "month";
				this.$page.find('[data-field="view"]').val("month");
				this.save_local_state();
				this.calendar.changeView(this.view_map.month, this.current_date);
				frappe.show_alert({ message: this.t("This calendar view is not available."), indicator: "orange" });
			}
		}
		this.update_range_label();
	}

	go_today() {
		this.current_date = new Date();
		if (this.is_year_view()) {
			this.render_year_view();
		} else if (this.calendar) {
			this.calendar.today();
		}
		this.render_mini_calendar();
		this.update_range_label();
	}

	go_to_date(date) {
		this.current_date = date;
		if (this.is_year_view()) {
			this.render_year_view();
		} else if (this.calendar) {
			this.calendar.gotoDate(date);
		}
		this.render_mini_calendar();
		this.update_range_label();
	}

	sync_from_calendar() {
		if (!this.calendar) return;
		this.current_date = this.calendar.getDate();
		this.render_mini_calendar();
		this.update_range_label();
	}

	update_range_label() {
		if (this.is_year_view()) {
			this.$page.find(".school-calendar-range-label").text(this.current_date.getFullYear());
			return;
		}
		if (!this.calendar) {
			this.$page.find(".school-calendar-range-label").text(this.format_month_year(this.current_date));
			return;
		}
		this.$page.find(".school-calendar-range-label").text(this.calendar.view.title);
	}

	refetch_events() {
		if (this.is_year_view()) {
			this.render_year_view();
			return;
		}
		if (this.calendar) {
			this.calendar.refetchEvents();
		}
	}

	render_year_view() {
		this.update_range_label();
		const year = this.current_date.getFullYear();
		const start = new Date(year, 0, 1);
		const end = new Date(year + 1, 0, 1);
		this.load_calendar_resources(start, end);
		this.$year_node.html(`<div class="school-year-loading">${this.t("Loading")}</div>`);

		frappe.call({
			method: "education.education.api.get_calendar_events",
			type: "GET",
			args: {
				start: this.to_system_datetime(start),
				end: this.to_system_datetime(end),
				calendars: JSON.stringify(Array.from(this.enabled_sources)),
				resource_filters: JSON.stringify(Array.from(this.resource_filters)),
				search: this.search_text,
				view: "year",
			},
			callback: (response) => {
				this.year_events = response.message || [];
				this.draw_year_grid();
			},
		});
	}

	draw_year_grid() {
		const year = this.current_date.getFullYear();
		const events_by_date = this.get_events_by_date(this.year_events);
		const month_cards = [];

		for (let month = 0; month < 12; month++) {
			month_cards.push(this.render_year_month(year, month, events_by_date));
		}

		this.$year_node.html(`<div class="school-year-grid">${month_cards.join("")}</div>`);
	}

	render_year_month(year, month, events_by_date) {
		const first = new Date(year, month, 1);
		const start = new Date(first);
		start.setDate(first.getDate() - ((first.getDay() + 6) % 7));
		const today_key = this.date_key(new Date());
		const selected_key = this.date_key(this.current_date);
		let cells = "";

		for (let index = 0; index < 42; index++) {
			const day = new Date(start);
			day.setDate(start.getDate() + index);
			const key = this.date_key(day);
			const count = (events_by_date[key] || []).length;
			const classes = [
				"school-year-day",
				day.getMonth() !== month ? "is-muted" : "",
				key === today_key ? "is-today" : "",
				key === selected_key ? "is-selected" : "",
				count ? "has-events" : "",
			]
				.filter(Boolean)
				.join(" ");
			cells += `
				<button class="${classes}" data-year-date="${key}" title="${count ? count + " " + this.t("events") : ""}">
					<span>${day.getDate()}</span>
					${count ? `<i>${count > 9 ? "9+" : count}</i>` : ""}
				</button>`;
		}

		return `
			<section class="school-year-month">
				<button class="school-year-month-title" data-year-month="${year}-${String(month + 1).padStart(2, "0")}-01">
					${this.format_month_name(first)}
				</button>
				<div class="school-year-weekdays">${this.get_weekday_labels()
					.map((day) => `<span>${day}</span>`)
					.join("")}</div>
				<div class="school-year-days">${cells}</div>
			</section>`;
	}

	get_events_by_date(events) {
		const by_date = {};
		(events || []).forEach((event) => {
			const start = new Date(event.start);
			if (Number.isNaN(start.getTime())) return;
			const end = event.end ? new Date(event.end) : new Date(start);
			const cursor = new Date(start.getFullYear(), start.getMonth(), start.getDate());
			const last = Number.isNaN(end.getTime())
				? new Date(cursor)
				: new Date(end.getFullYear(), end.getMonth(), end.getDate());
			if (event.allDay && event.end && last > cursor) {
				last.setDate(last.getDate() - 1);
			}

			let guard = 0;
			while (cursor <= last && guard < 370) {
				const key = this.date_key(cursor);
				if (!by_date[key]) by_date[key] = [];
				by_date[key].push(event);
				cursor.setDate(cursor.getDate() + 1);
				guard++;
			}
		});
		return by_date;
	}

	can_create_event() {
		return this.sources.some((source) => source.can_create);
	}

	can_create_source(source_id) {
		const source = this.sources.find((item) => item.id === source_id);
		return Boolean(source && source.can_create);
	}

	update_create_button_state() {
		this.$page.find('[data-action="create"]').toggleClass("is-disabled", !this.can_create_event());
	}

	open_create_dialog(options = {}) {
		if (!this.can_create_event()) {
			frappe.msgprint(this.t("You do not have permission to create calendar records."));
			return;
		}
		const creatable_sources = this.sources.filter((source) => source.can_create);
		if (creatable_sources.length === 1) {
			this.open_create_dialog_for_source(creatable_sources[0].id, options);
			return;
		}

		const source_options = creatable_sources.map((source) => ({
			value: source.id,
			label: this.t(source.label),
		}));
		const dialog = new frappe.ui.Dialog({
			title: this.t("Create"),
			fields: [
				{
					fieldtype: "Select",
					fieldname: "calendar_source",
					label: this.t("Calendar"),
					options: source_options,
					default: source_options[0].value,
				},
			],
			primary_action_label: this.t("Continue"),
			primary_action: (values) => {
				dialog.hide();
				this.open_create_dialog_for_source(values.calendar_source, options);
			},
		});
		dialog.show();
	}

	open_settings_dialog() {
		const dialog = new frappe.ui.Dialog({
			title: this.t("Calendar settings"),
			fields: [
				{ fieldtype: "Check", fieldname: "weekends", label: this.t("Show weekends") },
				{ fieldtype: "Check", fieldname: "compact_events", label: this.t("Compact event rows") },
			],
			primary_action_label: this.t("Apply"),
			primary_action: (values) => {
				this.settings.weekends = Boolean(values.weekends);
				this.settings.compact_events = Boolean(values.compact_events);
				this.apply_settings_classes();
				this.save_local_state();
				if (this.calendar) {
					this.calendar.setOption("weekends", this.settings.weekends);
					this.calendar.updateSize();
				}
				if (this.is_year_view()) {
					this.render_year_view();
				}
				dialog.hide();
			},
		});
		dialog.set_values({
			weekends: this.settings.weekends ? 1 : 0,
			compact_events: this.settings.compact_events ? 1 : 0,
		});
		dialog.show();
	}

	open_create_dialog_for_source(source, options = {}) {
		if (!this.can_create_source(source)) {
			frappe.msgprint(this.t("You do not have permission to create this calendar record."));
			return;
		}

		const start = options.start || this.current_date;
		const end = options.end || this.add_hours(start, 1);

		if (source === "course_schedule") {
			frappe.new_doc("Course Schedule", {
				schedule_date: this.to_system_datetime(start).split(" ")[0],
				from_time: this.to_system_datetime(start).split(" ")[1],
				to_time: this.to_system_datetime(end).split(" ")[1]
			});
			return;
		}

		frappe.new_doc("Event", {
			starts_on: this.to_system_datetime(start),
			ends_on: this.to_system_datetime(end),
			all_day: options.all_day ? 1 : 0
		});
	}

	open_course_schedule_dialog(options) {
		const start = options.start || new Date();
		const end = options.end || this.add_hours(start, 1);
		const dialog = new frappe.ui.Dialog({
			title: this.t("Create Course Schedule"),
			fields: [
				{
					fieldtype: "Link",
					fieldname: "student_group",
					label: this.t("Student Group"),
					options: "Student Group",
					reqd: 1,
				},
				{ fieldtype: "Link", fieldname: "course", label: this.t("Course"), options: "Course", reqd: 1 },
				{
					fieldtype: "Link",
					fieldname: "instructor",
					label: this.t("Instructor"),
					options: "Instructor",
					reqd: 1,
				},
				{ fieldtype: "Link", fieldname: "room", label: this.t("Room"), options: "Room", reqd: 1 },
				{ fieldtype: "Datetime", fieldname: "starts_on", label: this.t("Starts on"), reqd: 1 },
				{ fieldtype: "Datetime", fieldname: "ends_on", label: this.t("Ends on"), reqd: 1 },
				{
					fieldtype: "Select",
					fieldname: "class_schedule_color",
					label: this.t("Color"),
					options: this.get_color_options(),
					default: "blue",
				},
			],
			primary_action_label: this.t("Save"),
			primary_action: (values) => {
				frappe.call({
					method: "education.education.api.create_course_schedule_event",
					args: { data: values },
					callback: (response) => {
						dialog.hide();
						this.refetch_events();
						frappe.show_alert({ message: this.t("Course Schedule created"), indicator: "green" });
						if (response.message && response.message.name) {
							frappe.set_route("Form", "Course Schedule", response.message.name);
						}
					},
				});
			},
		});
		dialog.set_values({
			starts_on: this.to_system_datetime(start),
			ends_on: this.to_system_datetime(end),
			class_schedule_color: "blue",
		});
		dialog.show();
	}

	open_event_dialog(options) {
		const start = options.start || new Date();
		const end = options.end || this.add_hours(start, 1);
		const dialog = new frappe.ui.Dialog({
			title: options.name ? this.t("Edit event") : this.t("Create event"),
			fields: [
				{ fieldtype: "Data", fieldname: "title", label: this.t("Title"), reqd: 1 },
				{ fieldtype: "Datetime", fieldname: "starts_on", label: this.t("Starts on"), reqd: 1 },
				{ fieldtype: "Datetime", fieldname: "ends_on", label: this.t("Ends on"), reqd: 1 },
				{ fieldtype: "Check", fieldname: "all_day", label: this.t("All day") },
				{
					fieldtype: "Select",
					fieldname: "visibility",
					label: this.t("Visibility"),
					options: this.get_visibility_options(),
					default: "Private",
				},
				{ fieldtype: "Color", fieldname: "color", label: this.t("Color"), default: "#188038" },
				{
					fieldtype: "Select",
					fieldname: "status",
					label: this.t("Status"),
					options: this.get_status_options(),
					default: "Open",
				},
				{ fieldtype: "Small Text", fieldname: "description", label: this.t("Description") },
			],
			primary_action_label: this.t("Save"),
			primary_action: (values) => {
				const method = options.name
					? "education.education.api.update_calendar_event"
					: "education.education.api.create_calendar_event";
				const args = options.name ? { name: options.name, data: values } : { data: values };
				frappe.call({
					method,
					args,
					callback: () => {
						dialog.hide();
						this.refetch_events();
						frappe.show_alert({ message: this.t("Event saved"), indicator: "green" });
					},
				});
			},
		});
		dialog.set_values({
			title: options.title || "",
			starts_on: this.to_system_datetime(start),
			ends_on: this.to_system_datetime(end),
			all_day: options.all_day ? 1 : 0,
			visibility: options.visibility || "Private",
			color: options.color || "#188038",
			status: options.status || "Open",
			description: options.description || "",
		});
		dialog.show();
	}

	open_existing_event_dialog(name) {
		frappe.call({
			method: "education.education.api.get_calendar_event",
			args: { name },
			callback: (response) => {
				const event = response.message || {};
				this.open_event_dialog({
					name: event.name,
					title: event.title,
					start: event.starts_on,
					end: event.ends_on,
					all_day: event.all_day,
					visibility: event.visibility,
					color: event.color,
					status: event.status,
					description: event.description,
				});
			},
		});
	}

	open_event_popover(event, element) {
		this.close_popover();
		const props = event.extendedProps || {};
		const is_read_only = Boolean(props.read_only);
		const can_write = props.can_write === undefined ? !is_read_only : Boolean(props.can_write);
		const can_delete_record = props.can_delete === undefined ? !is_read_only : Boolean(props.can_delete);
		const can_edit = can_write;
		const can_delete = ["event", "course_schedule"].includes(props.source) && can_delete_record;
		const title = this.escape(event.title || this.t("Untitled Event"));
		const subtitle = this.escape(props.subtitle || this.format_event_time(event));
		const description = props.description ? this.escape(props.description) : "";
		const edit_action = can_edit
			? `<button class="school-icon-btn" data-popover-action="edit">${this.icon("edit", this.t("Edit"))}</button>`
			: "";
		const delete_action = can_delete
			? `<button class="school-icon-btn" data-popover-action="delete">${this.icon("delete", this.t("Delete"))}</button>`
			: "";

		this.$popover = $(`
			<div class="school-event-popover">
				<div class="school-popover-color" style="--event-color: ${this.escape(event.backgroundColor || event.borderColor || "#1a73e8")}"></div>
				<div class="school-popover-body">
					<div class="school-popover-actions">
						${edit_action}
						${delete_action}
					</div>
					<div class="school-popover-title">${title}</div>
					<div class="school-popover-time">${subtitle}</div>
					${description ? `<div class="school-popover-description">${description}</div>` : ""}
				</div>
			</div>
		`).appendTo(this.$page);

		this.position_popover(element);
		this.$popover.on("click", "[data-popover-action]", (click_event) => {
			const action = $(click_event.currentTarget).data("popover-action");
			if (action === "open") {
				frappe.set_route("Form", props.doctype, props.name);
			} else if (action === "edit") {
				if (props.source === "course_schedule") {
					frappe.set_route("Form", props.doctype, props.name);
				} else {
					this.open_existing_event_dialog(props.name);
				}
				this.close_popover();
			} else if (action === "delete") {
				this.confirm_delete(props);
			}
		});
	}

	position_popover(element) {
		const page_rect = this.$page[0].getBoundingClientRect();
		const event_rect = element.getBoundingClientRect();
		const width = 320;
		let left = event_rect.right - page_rect.left + 12;
		let top = event_rect.top - page_rect.top;
		if (left + width > page_rect.width) {
			left = event_rect.left - page_rect.left - width - 12;
		}
		if (left < 12) left = 12;
		if (top < 12) top = 12;
		this.$popover.css({ left, top });
	}

	close_popover() {
		if (this.$popover) {
			this.$popover.remove();
			this.$popover = null;
		}
	}

	confirm_delete(event_props) {
		const props =
			typeof event_props === "string"
				? { name: event_props, source: "event", doctype: "Event" }
				: event_props || {};
		const is_course_schedule = props.source === "course_schedule" || props.doctype === "Course Schedule";
		const confirm_message = is_course_schedule ? this.t("Delete this schedule?") : this.t("Delete this event?");
		const deleted_message = is_course_schedule ? this.t("Schedule deleted") : this.t("Event deleted");
		const args = { name: props.name };
		if (props.source) {
			args.source = props.source;
		}
		if (props.doctype) {
			args.doctype = props.doctype;
		}

		frappe.confirm(confirm_message, () => {
			frappe.call({
				method: "education.education.api.delete_calendar_event",
				args,
				callback: () => {
					this.close_popover();
					this.refetch_events();
					frappe.show_alert({ message: deleted_message, indicator: "red" });
				},
			});
		});
	}

	persist_event_move(info) {
		const props = info.event.extendedProps || {};
		if (props.source !== "event") {
			info.revert();
			return;
		}
		frappe.call({
			method: "education.education.api.update_calendar_event",
			args: {
				name: props.name,
				data: {
					title: info.event.title,
					starts_on: this.to_system_datetime(info.event.start),
					ends_on: this.to_system_datetime(info.event.end || this.add_hours(info.event.start, 1)),
					all_day: info.event.allDay ? 1 : 0,
					color: info.event.backgroundColor || "#188038",
					status: info.event.extendedProps.status || "Open",
				},
			},
			callback: () => this.refetch_events(),
			error: () => info.revert(),
		});
	}

	refresh() {
		if (this.calendar) {
			this.calendar.updateSize();
			this.refetch_events();
		}
	}

	destroy() {
		this.close_popover();
		clearTimeout(this.search_timer);
		clearTimeout(this.people_timer);
		this.$page && this.$page.off(".schoolCalendar");
		$(document).off(".schoolCalendar");
		if (this.calendar) {
			this.calendar.destroy();
			this.calendar = null;
		}
	}

	to_system_datetime(date) {
		if (!date) return null;
		if (typeof date === "string") return date;
		return frappe.datetime.convert_to_system_tz(date, true);
	}

	format_event_time(event) {
		if (!event.start) return "";
		const start = this.format_date_time(event.start);
		const end = event.end ? this.format_date_time(event.end) : "";
		return end ? `${start} - ${end}` : start;
	}

	format_date_time(date) {
		return new Intl.DateTimeFormat(this.get_date_locale(), {
			month: "short",
			day: "numeric",
			hour: "2-digit",
			minute: "2-digit",
		}).format(date);
	}

	format_month_year(date) {
		return new Intl.DateTimeFormat(this.get_date_locale(), {
			month: "long",
			year: "numeric",
		}).format(date);
	}

	format_month_name(date) {
		return new Intl.DateTimeFormat(this.get_date_locale(), {
			month: "long",
		}).format(date);
	}

	date_key(date) {
		const year = date.getFullYear();
		const month = String(date.getMonth() + 1).padStart(2, "0");
		const day = String(date.getDate()).padStart(2, "0");
		return `${year}-${month}-${day}`;
	}

	add_hours(date, hours) {
		const next = new Date(date);
		next.setHours(next.getHours() + hours);
		return next;
	}

	add_days(date, days) {
		const next = new Date(date);
		next.setDate(next.getDate() + days);
		return next;
	}

	add_months(date, months) {
		const next = new Date(date);
		next.setMonth(next.getMonth() + months);
		return next;
	}
}
