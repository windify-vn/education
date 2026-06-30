# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt


from ast import If
import json

import frappe
from frappe import _
from frappe.email.doctype.email_group.email_group import add_subscribers
from frappe.model.mapper import get_mapped_doc
from frappe.utils import add_days, cstr, flt, get_datetime, getdate, today, to_timedelta
from frappe.utils.dateutils import get_dates_from_timegrain
from frappe.utils.file_manager import save_file


def get_course(program):
	"""Return list of courses for a particular program
	:param program: Program
	"""
	courses = frappe.db.sql(
		"""select course, course_name from `tabProgram Course` where parent=%s""",
		(program),
		as_dict=1,
	)
	return courses


@frappe.whitelist()
def enroll_student(source_name):
	"""Creates a Student Record and returns a Program Enrollment.

	:param source_name: Student Applicant.
	"""
	frappe.publish_realtime(
		"enroll_student_progress", {"progress": [1, 4]}, user=frappe.session.user
	)
	student = get_mapped_doc(
		"Student Applicant",
		source_name,
		{
			"Student Applicant": {
				"doctype": "Student",
				"field_map": {
					"name": "student_applicant",
				},
			}
		},
		ignore_permissions=True,
	)
	student.save()

	student_applicant = frappe.db.get_value(
		"Student Applicant",
		source_name,
		["student_category", "program", "academic_year"],
		as_dict=True,
	)
	program_enrollment = frappe.new_doc("Program Enrollment")
	program_enrollment.student = student.name
	program_enrollment.student_category = student_applicant.student_category
	program_enrollment.student_name = student.student_name
	program_enrollment.program = student_applicant.program
	program_enrollment.academic_year = student_applicant.academic_year
	program_enrollment.save()

	frappe.publish_realtime(
		"enroll_student_progress", {"progress": [2, 4]}, user=frappe.session.user
	)
	return program_enrollment


@frappe.whitelist()
def check_attendance_records_exist(course_schedule=None, student_group=None, date=None):
	"""Check if Attendance Records are made against the specified Course Schedule or Student Group for given date.

	:param course_schedule: Course Schedule.
	:param student_group: Student Group.
	:param date: Date.
	"""
	if course_schedule:
		return frappe.get_list(
			"Student Attendance", filters={"course_schedule": course_schedule}
		)
	else:
		return frappe.get_list(
			"Student Attendance", filters={"student_group": student_group, "date": date}
		)


@frappe.whitelist()
def course_schedule_has_attendance(course_schedule):
	if not course_schedule:
		return 0

	if not frappe.has_permission("Course Schedule", "read", doc=course_schedule):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	return 1 if frappe.db.exists(
		"Student Attendance",
		{"course_schedule": course_schedule, "docstatus": ("!=", 2)},
	) else 0


@frappe.whitelist()
def mark_attendance(
	students_present, students_absent, course_schedule=None, student_group=None, date=None
):
	"""Creates Multiple Attendance Records.

	:param students_present: Students Present JSON.
	:param students_absent: Students Absent JSON.
	:param course_schedule: Course Schedule.
	:param student_group: Student Group.
	:param date: Date.
	"""
	if student_group:
		academic_year = frappe.db.get_value("Student Group", student_group, "academic_year")
		if academic_year:
			year_start_date, year_end_date = frappe.db.get_value(
				"Academic Year", academic_year, ["year_start_date", "year_end_date"]
			)
			if getdate(date) < getdate(year_start_date) or getdate(date) > getdate(
				year_end_date
			):
				frappe.throw(
					_("Attendance cannot be marked outside of Academic Year {0}").format(academic_year)
				)

	present = json.loads(students_present)
	absent = json.loads(students_absent)

	for d in present:
		make_attendance_records(
			d["student"], d["student_name"], "Present", course_schedule, student_group, date
		)

	for d in absent:
		make_attendance_records(
			d["student"], d["student_name"], "Absent", course_schedule, student_group, date
		)

	frappe.db.commit()
	frappe.msgprint(_("Attendance has been marked successfully."))


def make_attendance_records(
	student, student_name, status, course_schedule=None, student_group=None, date=None, leave_application=None
):
	"""Creates Attendance Record.

	:param student: Student.
	:param student_name: Student Name.
	:param course_schedule: Course Schedule.
	:param status: Status (Present/Absent/Leave).
	:param leave_application: Student Leave Application (optional, for Leave status).
	"""
	student_attendance = frappe.new_doc("Student Attendance")
	student_attendance.student = student
	student_attendance.student_name = student_name
	student_attendance.course_schedule = course_schedule
	student_attendance.student_group = student_group
	student_attendance.date = date
	student_attendance.status = status
	if leave_application:
		student_attendance.leave_application = leave_application
	student_attendance.flags.ignore_permissions = True
	student_attendance.save()
	student_attendance.submit()


@frappe.whitelist()
def get_student_guardians(student):
	"""Returns List of Guardians of a Student.

	:param student: Student.
	"""
	guardians = frappe.get_all(
		"Student Guardian", fields=["guardian"], filters={"parent": student}
	)
	return guardians


@frappe.whitelist()
def get_student_group_students(student_group, include_inactive=0):
	"""Returns List of student, student_name in Student Group.

	:param student_group: Student Group.
	"""
	if include_inactive:
		students = frappe.get_all(
			"Student Group Student",
			fields=["student", "student_name"],
			filters={"parent": student_group},
			order_by="group_roll_number",
		)
	else:
		students = frappe.get_all(
			"Student Group Student",
			fields=["student", "student_name"],
			filters={"parent": student_group, "active": 1},
			order_by="group_roll_number",
		)
	return students


@frappe.whitelist()
def get_fee_structure(program, academic_term=None):
	"""Returns Fee Structure.

	:param program: Program.
	:param academic_term: Academic Term.
	"""
	fee_structure = frappe.db.get_values(
		"Fee Structure",
		{"program": program, "academic_term": academic_term},
		"name",
		as_dict=True,
	)
	return fee_structure[0].name if fee_structure else None


@frappe.whitelist()
def get_fee_components(fee_structure):
	"""Returns Fee Components.

	:param fee_structure: Fee Structure.
	"""
	if fee_structure:
		fs = frappe.get_all(
			"Fee Component",
			fields=["fees_category", "description", "amount"],
			filters={"parent": fee_structure},
			order_by="idx",
		)
		return fs


@frappe.whitelist()
def get_fee_schedule(program, student_category=None):
	"""Returns Fee Schedule.

	:param program: Program.
	:param student_category: Student Category
	"""
	fs = frappe.get_all(
		"Program Fee",
		fields=["academic_term", "fee_schedule", "due_date", "amount"],
		filters={"parent": program, "student_category": student_category},
		order_by="idx",
	)
	return fs


@frappe.whitelist()
def collect_fees(fees, amt):
	paid_amount = flt(amt) + flt(frappe.db.get_value("Fees", fees, "paid_amount"))
	total_amount = flt(frappe.db.get_value("Fees", fees, "total_amount"))
	frappe.db.set_value("Fees", fees, "paid_amount", paid_amount)
	frappe.db.set_value("Fees", fees, "outstanding_amount", (total_amount - paid_amount))
	return paid_amount


@frappe.whitelist()
def get_course_schedule_events(start, end, filters=None):
	"""Returns events for Course Schedule Calendar view rendering.

	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from frappe.desk.calendar import get_event_conditions

	conditions = get_event_conditions("Course Schedule", filters)

	data = frappe.db.sql(
		"""select name, course, color,
			timestamp(schedule_date, from_time) as from_time,
			timestamp(schedule_date, to_time) as to_time,
			room, student_group, instructor_name, 0 as 'allDay'
		from `tabCourse Schedule`
		where ( schedule_date between %(start)s and %(end)s )
		{conditions}""".format(
			conditions=conditions
		),
		{"start": start, "end": end},
		as_dict=True,
		update={"allDay": 0},
	)

	# Format title with course, instructor_name, and room on separate lines with CSS styling
	for event in data:
		title_parts = []
		if event.get('course'):
			title_parts.append(f'Khóa học: {event.get("course")}')
		if event.get('student_group'):
			title_parts.append(f'Lớp: {event.get("student_group")}')
		if event.get('instructor_name'):
			title_parts.append(f'Giáo viên: {event.get("instructor_name")}')
		if event.get('room'):
			title_parts.append(f'Phòng: {event.get("room")}')
		event['title'] = '\n'.join(title_parts)

	return data


SCHOOL_CALENDAR_FALLBACK_LANGUAGE = "vi"
SCHOOL_CALENDAR_SUPPORTED_LANGUAGES = {"en", "vi"}
SCHOOL_CALENDAR_VI_MESSAGES = {
	"Course": "Khóa học",
	"Course Schedule": "Lịch dạy",
	"Course Schedule must start and end on the same date": "Lịch dạy phải bắt đầu và kết thúc trong cùng một ngày",
	"End date must be after start date": "Thời gian kết thúc phải sau thời gian bắt đầu",
	"Missing calendar date range": "Thiếu khoảng thời gian của lịch",
	"My Events": "Sự kiện của tôi",
	"Not permitted to create course schedules": "Không có quyền tạo lịch dạy",
	"Not permitted to create events": "Không có quyền tạo sự kiện",
	"Not permitted to delete this course schedule": "Không có quyền xóa lịch dạy này",
	"Not permitted to delete this event": "Không có quyền xóa sự kiện này",
	"Not permitted to read this event": "Không có quyền xem sự kiện này",
	"Not permitted to update this event": "Không có quyền cập nhật sự kiện này",
	"Room": "Phòng",
	"This calendar record cannot be deleted": "Không thể xóa bản ghi lịch này",
	"Student Group": "Lớp học",
	"Title is required": "Tiêu đề là bắt buộc",
	"Untitled Event": "Sự kiện chưa có tiêu đề",
	"{0} is required": "{0} là bắt buộc",
}


def _school_calendar_language():
	language = getattr(frappe.local, "lang", None) or frappe.db.get_value("User", frappe.session.user, "language")
	language = cstr(language or SCHOOL_CALENDAR_FALLBACK_LANGUAGE).replace("_", "-").lower().split("-")[0]
	return language if language in SCHOOL_CALENDAR_SUPPORTED_LANGUAGES else SCHOOL_CALENDAR_FALLBACK_LANGUAGE


def _school_calendar_t(message):
	if _school_calendar_language() == "en":
		return _(message)

	if cstr(getattr(frappe.local, "lang", None)).replace("_", "-").lower().split("-")[0] == "vi":
		translated = _(message)
		if translated and translated != message:
			return translated

	return SCHOOL_CALENDAR_VI_MESSAGES.get(message, message)


def _school_calendar_json(value, fallback=None):
	if value in (None, ""):
		return fallback
	if isinstance(value, str):
		return frappe.parse_json(value)
	return value


def _school_calendar_source_enabled(calendars, source):
	return not calendars or source in calendars


def _school_calendar_date(value):
	if not value:
		frappe.throw(_school_calendar_t("Missing calendar date range"))
	return get_datetime(value)


def _school_calendar_normalize_all_day_end(starts_on, ends_on, all_day):
	if not all_day:
		return ends_on
	if getdate(ends_on) > getdate(starts_on) and ends_on.strftime("%H:%M:%S") == "00:00:00":
		return get_datetime(f"{add_days(getdate(ends_on), -1)} 23:59:59")
	return ends_on


def _school_calendar_color(color):
	color_map = {
		"blue": "#1a73e8",
		"green": "#188038",
		"red": "#d93025",
		"orange": "#f29900",
		"yellow": "#fbbc04",
		"teal": "#009688",
		"violet": "#7b1fa2",
		"cyan": "#0097a7",
		"amber": "#f9ab00",
		"pink": "#d81b60",
		"purple": "#8e24aa",
	}
	if color and str(color).startswith("#"):
		return color
	return color_map.get(color or "blue", color_map["blue"])


def _school_calendar_search_match(row, search, fields):
	if not search:
		return True
	search = search.lower()
	return any(search in cstr(row.get(field)).lower() for field in fields)


def _school_calendar_child_table_options(parent_doctype, table_fieldname):
	return frappe.db.get_value(
		"DocField",
		{"parent": parent_doctype, "fieldname": table_fieldname, "fieldtype": "Table"},
		"options",
	)


def _school_calendar_get_resource_map(schedules):
	student_groups = sorted({schedule.student_group for schedule in schedules if schedule.student_group})
	schedule_names = sorted({schedule.name for schedule in schedules if schedule.name})
	resource_map = {
		schedule.name: {"instructor": set(), "teaching_assistant": set()}
		for schedule in schedules
	}

	if student_groups:
		for row in frappe.get_all(
			"Student Group Instructor",
			fields=["parent", "instructor"],
			filters={"parent": ["in", student_groups]},
		):
			for schedule in schedules:
				if schedule.student_group == row.parent and row.instructor:
					resource_map[schedule.name]["instructor"].add(row.instructor)

	student_group_assistant_doctype = _school_calendar_child_table_options(
		"Student Group", "teaching_assistants"
	)
	if student_group_assistant_doctype and student_groups:
		for row in frappe.get_all(
			student_group_assistant_doctype,
			fields=["parent", "employee"],
			filters={"parent": ["in", student_groups]},
		):
			for schedule in schedules:
				if schedule.student_group == row.parent and row.employee:
					resource_map[schedule.name]["teaching_assistant"].add(row.employee)

	course_schedule_assistant_doctype = _school_calendar_child_table_options(
		"Course Schedule", "teaching_assistants"
	)
	if course_schedule_assistant_doctype and schedule_names:
		for row in frappe.get_all(
			course_schedule_assistant_doctype,
			fields=["parent", "employee"],
			filters={"parent": ["in", schedule_names]},
		):
			if row.parent in resource_map and row.employee:
				resource_map[row.parent]["teaching_assistant"].add(row.employee)

	return resource_map


def _school_calendar_resource_match(schedule, resource_filters, resource_map):
	if not resource_filters:
		return True

	resources = resource_map.get(schedule.name, {})
	instructors = set(resources.get("instructor") or [])
	if schedule.get("instructor"):
		instructors.add(schedule.get("instructor"))
	teaching_assistants = set(resources.get("teaching_assistant") or [])

	for resource in resource_filters:
		if "::" in resource:
			resource_type, resource_name = resource.split("::", 1)
			if resource_type == "instructor" and resource_name in instructors:
				return True
			if resource_type == "teaching_assistant" and resource_name in teaching_assistants:
				return True
		elif resource == "instructor" and instructors:
			return True
		elif resource == "teaching_assistant" and teaching_assistants:
			return True
	return False


def _school_calendar_resource_key(resource_type, resource_name):
	return f"{resource_type}::{resource_name}"


def _school_calendar_get_resource_options(schedules, resource_map):
	instructor_counts = {}
	assistant_counts = {}

	for schedule in schedules:
		resources = resource_map.get(schedule.name, {})
		instructors = set(resources.get("instructor") or [])
		if schedule.get("instructor"):
			instructors.add(schedule.get("instructor"))
		for instructor in instructors:
			instructor_counts[instructor] = instructor_counts.get(instructor, 0) + 1

		for assistant in resources.get("teaching_assistant") or []:
			assistant_counts[assistant] = assistant_counts.get(assistant, 0) + 1

	instructor_labels = {}
	if instructor_counts:
		for row in frappe.get_all(
			"Instructor",
			fields=["name", "instructor_name"],
			filters={"name": ["in", list(instructor_counts)]},
		):
			instructor_labels[row.name] = row.instructor_name or row.name

	assistant_labels = {}
	if assistant_counts:
		for row in frappe.get_all(
			"Employee",
			fields=["name", "employee_name"],
			filters={"name": ["in", list(assistant_counts)]},
		):
			assistant_labels[row.name] = row.employee_name or row.name

	def build_options(resource_type, counts, labels, color):
		return sorted(
			[
				{
					"id": _school_calendar_resource_key(resource_type, name),
					"name": name,
					"label": labels.get(name) or name,
					"type": resource_type,
					"count": count,
					"color": color,
				}
				for name, count in counts.items()
			],
			key=lambda row: cstr(row.get("label")).lower(),
		)

	return {
		"instructor": build_options("instructor", instructor_counts, instructor_labels, "#1a73e8"),
		"teaching_assistant": build_options(
			"teaching_assistant", assistant_counts, assistant_labels, "#8e24aa"
		),
	}


@frappe.whitelist()
def get_calendar_sources():
	"""Return calendar sources available to the current user for the Desk calendar page."""
	sources = []

	if frappe.has_permission("Course Schedule", "read"):
		sources.append(
			{
				"id": "course_schedule",
				"label": _school_calendar_t("Course Schedule"),
				"doctype": "Course Schedule",
				"color": "#1a73e8",
				"checked": 1,
				"read_only": 0 if frappe.has_permission("Course Schedule", "write") else 1,
				"can_create": 1 if frappe.has_permission("Course Schedule", "create") else 0,
			}
		)

	if frappe.has_permission("Event", "read"):
		sources.append(
			{
				"id": "event",
				"label": _school_calendar_t("My Events"),
				"doctype": "Event",
				"color": "#188038",
				"checked": 1,
				"read_only": 0 if frappe.has_permission("Event", "create") else 1,
				"can_create": 1 if frappe.has_permission("Event", "create") else 0,
			}
		)

	return sources


@frappe.whitelist()
def get_calendar_resources(start, end, calendars=None):
	"""Return instructors and assistants present in Course Schedule events for the current range."""
	start_dt = _school_calendar_date(start)
	end_dt = _school_calendar_date(end)
	calendars = _school_calendar_json(calendars, []) or []

	if not _school_calendar_source_enabled(calendars, "course_schedule") or not frappe.has_permission(
		"Course Schedule", "read"
	):
		return {"instructor": [], "teaching_assistant": []}

	schedules = frappe.get_list(
		"Course Schedule",
		fields=["name", "student_group", "instructor"],
		filters={"schedule_date": ["between", [getdate(start_dt), getdate(end_dt)]]},
		order_by="schedule_date asc, from_time asc",
	)
	resource_map = _school_calendar_get_resource_map(schedules)
	return _school_calendar_get_resource_options(schedules, resource_map)


@frappe.whitelist()
def get_calendar_events(start, end, calendars=None, search=None, view=None, resource_filters=None):
	"""Return calendar events for the custom Academy Calendar Desk page."""
	start_dt = _school_calendar_date(start)
	end_dt = _school_calendar_date(end)
	if end_dt < start_dt:
		frappe.throw(_school_calendar_t("End date must be after start date"))

	calendars = _school_calendar_json(calendars, []) or []
	resource_filters = set(_school_calendar_json(resource_filters, ["instructor", "teaching_assistant"]) or [])
	search = cstr(search).strip()
	events = []

	if _school_calendar_source_enabled(calendars, "course_schedule") and frappe.has_permission(
		"Course Schedule", "read"
	):
		schedules = frappe.get_list(
			"Course Schedule",
			fields=[
				"name",
				"course",
				"room",
				"student_group",
				"instructor",
				"instructor_name",
				"class_schedule_color",
				"schedule_date",
				"from_time",
				"to_time",
			],
			filters={"schedule_date": ["between", [getdate(start_dt), getdate(end_dt)]]},
			order_by="schedule_date asc, from_time asc",
		)
		resource_map = _school_calendar_get_resource_map(schedules)
		for schedule in schedules:
			if not _school_calendar_resource_match(schedule, resource_filters, resource_map):
				continue
			if not _school_calendar_search_match(
				schedule, search, ["course", "room", "student_group", "instructor_name"]
			):
				continue
			starts_on = get_datetime(f"{schedule.schedule_date} {schedule.from_time}")
			ends_on = get_datetime(f"{schedule.schedule_date} {schedule.to_time}")
			title = schedule.get("course") or _school_calendar_t("Course Schedule")
			subtitle = " · ".join(
				filter(None, [schedule.get("student_group"), schedule.get("instructor_name"), schedule.get("room")])
			)
			can_write = 1 if frappe.has_permission("Course Schedule", "write", doc=schedule.name) else 0
			can_delete = 1 if frappe.has_permission("Course Schedule", "delete", doc=schedule.name) else 0
			events.append(
				{
					"id": f"course_schedule::{schedule.name}",
					"name": schedule.name,
					"doctype": "Course Schedule",
					"source": "course_schedule",
					"title": title,
					"subtitle": subtitle,
					"start": starts_on,
					"end": ends_on,
					"allDay": 0,
					"color": _school_calendar_color(schedule.get("class_schedule_color")),
					"editable": False,
					"extendedProps": {
						"doctype": "Course Schedule",
						"name": schedule.name,
						"source": "course_schedule",
						"subtitle": subtitle,
						"read_only": 0 if can_write else 1,
						"can_write": can_write,
						"can_delete": can_delete,
					},
				}
			)

	if _school_calendar_source_enabled(calendars, "event") and frappe.has_permission("Event", "read"):
		event_rows = frappe.get_list(
			"Event",
			fields=[
				"name",
				"subject",
				"starts_on",
				"ends_on",
				"all_day",
				"event_type",
				"color",
				"description",
				"status",
				"owner",
			],
			filters=[["Event", "starts_on", "<=", end_dt]],
			or_filters=[
				["Event", "ends_on", ">=", start_dt],
				["Event", "ends_on", "is", "not set"],
			],
			order_by="starts_on asc",
		)
		for event in event_rows:
			if event.get("event_type") == "Private" and event.get("owner") != frappe.session.user:
				continue
			if not _school_calendar_search_match(event, search, ["subject", "description", "status"]):
				continue
			event_start = get_datetime(event.get("starts_on"))
			event_end = get_datetime(event.get("ends_on") or event.get("starts_on"))
			if event_end < start_dt or event_start > end_dt:
				continue
			color = event.get("color") or "#188038"
			if event.get("all_day") and getdate(event_end) <= getdate(event.get("starts_on")):
				event_end = add_days(getdate(event.get("starts_on")), 1)
			can_write = 1 if frappe.has_permission("Event", "write", event.name) else 0
			can_delete = 1 if frappe.has_permission("Event", "delete", event.name) else 0
			events.append(
				{
					"id": f"event::{event.name}",
					"name": event.name,
					"doctype": "Event",
					"source": "event",
					"title": event.get("subject") or _school_calendar_t("Untitled Event"),
					"start": event_start,
					"end": event_end,
					"allDay": event.get("all_day"),
					"color": color,
					"editable": Boolean(can_write),
					"extendedProps": {
						"doctype": "Event",
						"name": event.name,
						"source": "event",
						"description": event.get("description"),
						"status": event.get("status"),
						"read_only": 0 if can_write else 1,
						"can_write": can_write,
						"can_delete": can_delete,
					},
				}
			)

	return events


@frappe.whitelist()
def get_calendar_event(name):
	"""Return a single editable Event payload for the custom Academy Calendar page."""
	name = cstr(name).replace("event::", "")
	doc = frappe.get_doc("Event", name)
	if not doc.has_permission("read"):
		frappe.throw(_school_calendar_t("Not permitted to read this event"), frappe.PermissionError)

	return {
		"name": doc.name,
		"title": doc.subject,
		"starts_on": doc.starts_on,
		"ends_on": doc.ends_on or doc.starts_on,
		"all_day": doc.all_day,
		"visibility": doc.event_type or "Private",
		"event_category": doc.event_category or "Event",
		"color": doc.color or "#188038",
		"description": doc.description or "",
		"status": doc.status or "Open",
	}


def _school_calendar_event_doc(data, doc=None):
	data = _school_calendar_json(data, {}) or {}
	subject = cstr(data.get("title") or data.get("subject")).strip()
	if not subject:
		frappe.throw(_school_calendar_t("Title is required"))

	starts_on = _school_calendar_date(data.get("starts_on") or data.get("start"))
	ends_on = data.get("ends_on") or data.get("end")
	ends_on = get_datetime(ends_on) if ends_on else starts_on
	if ends_on < starts_on:
		frappe.throw(_school_calendar_t("End date must be after start date"))
	all_day = 1 if data.get("all_day") or data.get("allDay") else 0
	ends_on = _school_calendar_normalize_all_day_end(starts_on, ends_on, all_day)

	doc = doc or frappe.new_doc("Event")
	doc.subject = subject
	doc.starts_on = starts_on
	doc.ends_on = ends_on
	doc.all_day = all_day
	doc.event_type = data.get("event_type") or data.get("visibility") or doc.event_type or "Private"
	doc.event_category = data.get("event_category") or doc.event_category or "Event"
	doc.color = data.get("color") or doc.color or "#188038"
	doc.description = data.get("description") or ""
	doc.status = data.get("status") or doc.status or "Open"
	return doc


def _school_calendar_course_schedule_doc(data, doc=None):
	data = _school_calendar_json(data, {}) or {}
	starts_on = _school_calendar_date(data.get("starts_on") or data.get("start"))
	ends_on = _school_calendar_date(data.get("ends_on") or data.get("end"))
	if ends_on <= starts_on:
		frappe.throw(_school_calendar_t("End date must be after start date"))
	if getdate(starts_on) != getdate(ends_on):
		frappe.throw(_school_calendar_t("Course Schedule must start and end on the same date"))

	required_fields = ["student_group", "room"]
	for fieldname in required_fields:
		if not data.get(fieldname):
			field_label = _school_calendar_t(fieldname.replace("_", " ").title())
			frappe.throw(_school_calendar_t("{0} is required").format(field_label))

	doc = doc or frappe.new_doc("Course Schedule")
	doc.student_group = data.get("student_group")
	doc.course = data.get("course")
	doc.instructor = data.get("instructor")
	doc.room = data.get("room")
	doc.schedule_date = getdate(starts_on)
	doc.from_time = to_timedelta(starts_on.time())
	doc.to_time = to_timedelta(ends_on.time())
	doc.duration = int((ends_on - starts_on).total_seconds() / 60)
	doc.class_schedule_color = data.get("class_schedule_color") or doc.class_schedule_color or "blue"
	return doc


@frappe.whitelist()
def create_calendar_event(data):
	"""Create a core Event from the custom Academy Calendar page."""
	if not frappe.has_permission("Event", "create"):
		frappe.throw(_school_calendar_t("Not permitted to create events"), frappe.PermissionError)
	doc = _school_calendar_event_doc(data)
	doc.insert()
	return {"name": doc.name}


@frappe.whitelist()
def create_course_schedule_event(data):
	"""Create a Course Schedule from the custom Academy Calendar page."""
	if not frappe.has_permission("Course Schedule", "create"):
		frappe.throw(_school_calendar_t("Not permitted to create course schedules"), frappe.PermissionError)
	doc = _school_calendar_course_schedule_doc(data)
	doc.insert()
	return {"name": doc.name}


@frappe.whitelist()
def update_calendar_event(name, data):
	"""Update a core Event from the custom Academy Calendar page."""
	name = cstr(name).replace("event::", "")
	doc = frappe.get_doc("Event", name)
	if not doc.has_permission("write"):
		frappe.throw(_school_calendar_t("Not permitted to update this event"), frappe.PermissionError)
	doc = _school_calendar_event_doc(data, doc)
	doc.save()
	return {"name": doc.name}


@frappe.whitelist()
def delete_calendar_event(name, doctype=None, source=None):
	"""Delete a supported calendar record from the custom Academy Calendar page."""
	name = cstr(name)
	doctype = cstr(doctype)
	source = cstr(source)

	if name.startswith("course_schedule::"):
		source = "course_schedule"
		name = name.replace("course_schedule::", "", 1)
	elif name.startswith("event::"):
		source = "event"
		name = name.replace("event::", "", 1)

	if source == "course_schedule" or doctype == "Course Schedule":
		doctype = "Course Schedule"
		not_permitted_message = "Not permitted to delete this course schedule"
	elif source in ("", "event") and doctype in ("", "Event"):
		doctype = "Event"
		not_permitted_message = "Not permitted to delete this event"
	else:
		frappe.throw(_school_calendar_t("This calendar record cannot be deleted"), frappe.PermissionError)

	doc = frappe.get_doc(doctype, name)
	if not doc.has_permission("delete"):
		frappe.throw(_school_calendar_t(not_permitted_message), frappe.PermissionError)
	frappe.delete_doc(doctype, doc.name)
	return {"name": doc.name}


@frappe.whitelist()
def get_people(search=None):
	"""Return people-like records for the calendar sidebar search."""
	search = cstr(search).strip()
	if not search:
		return []

	people = []
	if frappe.has_permission("Instructor", "read"):
		for instructor in frappe.get_list(
			"Instructor",
			fields=["name", "instructor_name"],
			filters={"instructor_name": ["like", f"%{search}%"]},
			limit_page_length=10,
		):
			people.append(
				{
					"doctype": "Instructor",
					"name": instructor.name,
					"label": instructor.instructor_name or instructor.name,
				}
			)

	if frappe.has_permission("User", "read") and len(people) < 10:
		for user in frappe.get_list(
			"User",
			fields=["name", "full_name"],
			filters={"enabled": 1, "full_name": ["like", f"%{search}%"]},
			limit_page_length=10 - len(people),
		):
			people.append(
				{
					"doctype": "User",
					"name": user.name,
					"label": user.full_name or user.name,
				}
			)

	return people


@frappe.whitelist()
def get_assessment_criteria(course):
	"""Returns Assessmemt Criteria and their Weightage from Course Master.

	:param Course: Course
	"""
	return frappe.get_all(
		"Course Assessment Criteria",
		fields=["assessment_criteria", "weightage"],
		filters={"parent": course},
		order_by="idx",
	)


@frappe.whitelist()
def get_assessment_students(assessment_plan, student_group):
	student_list = get_student_group_students(student_group)
	for i, student in enumerate(student_list):
		result = get_result(student.student, assessment_plan)
		if result:
			student_result = {}
			for d in result.details:
				student_result.update({d.assessment_criteria: [cstr(d.score), d.grade]})
			student_result.update(
				{"total_score": [cstr(result.total_score), result.grade], "comment": result.comment}
			)
			student.update(
				{
					"assessment_details": student_result,
					"docstatus": result.docstatus,
					"name": result.name,
				}
			)
		else:
			student.update({"assessment_details": None})
	return student_list


@frappe.whitelist()
def get_assessment_details(assessment_plan):
	"""Returns Assessment Criteria  and Maximum Score from Assessment Plan Master.

	:param Assessment Plan: Assessment Plan
	"""
	return frappe.get_all(
		"Assessment Plan Criteria",
		fields=["assessment_criteria", "maximum_score", "docstatus"],
		filters={"parent": assessment_plan},
		order_by="idx",
	)


@frappe.whitelist()
def get_assessment_results_for_student(student, course=None, start=0, page_length=20):
	"""Returns all Assessment Results for a given student with pagination
	
	:param Student: Student
	:param course: Optional course name to filter results
	:param start: Start index for pagination
	:param page_length: Number of items per page
	"""
	filters = {
		"student": student,
		"docstatus": ("!=", 2),
	}
	
	if course:
		filters["course"] = course

	return frappe.get_all(
		"Assessment Result",
		fields=[
			"name",
			"student",
			"assessment_group",
			"student_group",
			"course",
			"creation",
			"total_score",
			"maximum_score",
			"grade",
			"docstatus"
		],
		filters=filters,
		order_by="creation desc",
		start=start,
		limit=page_length
	)


@frappe.whitelist()
def get_assessment_results_count(student, course=None):
	"""Returns count of Assessment Results for a given student
	
	:param Student: Student
	:param course: Optional course name to filter results
	"""
	filters = {
		"student": student,
		"docstatus": ("!=", 2),
	}
	
	if course:
		filters["course"] = course

	return frappe.db.count("Assessment Result", filters)


@frappe.whitelist()
def get_assessment_result_courses(student):
	"""Returns distinct course list from Assessment Result for a given student.

	:param Student: Student
	"""
	rows = frappe.db.sql(
		"""
		select distinct course
		from `tabAssessment Result`
		where student = %s
			and docstatus != 2
			and ifnull(course, '') != ''
		order by course
		""",
		(student,),
		as_list=True,
	)
	return [r[0] for r in rows]


@frappe.whitelist()
def get_result(student, assessment_plan):
	"""Returns Submitted Result of given student for specified Assessment Plan

	:param Student: Student
	:param Assessment Plan: Assessment Plan
	"""
	results = frappe.get_all(
		"Assessment Result",
		filters={
			"student": student,
			"assessment_plan": assessment_plan,
			"docstatus": ("!=", 2),
		},
	)
	if results:
		return frappe.get_doc("Assessment Result", results[0])
	else:
		return None


@frappe.whitelist()
def get_grade(grading_scale, percentage):
	"""Returns Grade based on the Grading Scale and Score.

	:param Grading Scale: Grading Scale
	:param Percentage: Score Percentage Percentage
	"""
	grading_scale_intervals = {}
	if not hasattr(frappe.local, "grading_scale"):
		grading_scale = frappe.get_all(
			"Grading Scale Interval",
			fields=["grade_code", "threshold"],
			filters={"parent": grading_scale},
		)
		frappe.local.grading_scale = grading_scale
	for d in frappe.local.grading_scale:
		grading_scale_intervals.update({d.threshold: d.grade_code})
	intervals = sorted(grading_scale_intervals.keys(), key=float, reverse=True)
	for interval in intervals:
		if flt(percentage) >= interval:
			grade = grading_scale_intervals.get(interval)
			break
		else:
			grade = ""
	return grade


@frappe.whitelist()
def mark_assessment_result(assessment_plan, scores):
	student_score = json.loads(scores)
	assessment_details = []
	for criteria in student_score.get("assessment_details"):
		assessment_details.append(
			{
				"assessment_criteria": criteria,
				"score": flt(student_score["assessment_details"][criteria]),
			}
		)
	assessment_result = get_assessment_result_doc(
		student_score["student"], assessment_plan
	)
	assessment_result.update(
		{
			"student": student_score.get("student"),
			"assessment_plan": assessment_plan,
			"comment": student_score.get("comment"),
			"total_score": student_score.get("total_score"),
			"details": assessment_details,
		}
	)
	assessment_result.save()
	details = {}
	for d in assessment_result.details:
		details.update({d.assessment_criteria: d.grade})
	assessment_result_dict = {
		"name": assessment_result.name,
		"student": assessment_result.student,
		"total_score": assessment_result.total_score,
		"grade": assessment_result.grade,
		"details": details,
	}
	return assessment_result_dict


@frappe.whitelist()
def submit_assessment_results(assessment_plan, student_group):
	total_result = 0
	student_list = get_student_group_students(student_group)
	for i, student in enumerate(student_list):
		doc = get_result(student.student, assessment_plan)
		if doc and doc.docstatus == 0:
			total_result += 1
			doc.submit()
	return total_result


def get_assessment_result_doc(student, assessment_plan):
	assessment_result = frappe.get_all(
		"Assessment Result",
		filters={
			"student": student,
			"assessment_plan": assessment_plan,
			"docstatus": ("!=", 2),
		},
	)
	if assessment_result:
		doc = frappe.get_doc("Assessment Result", assessment_result[0])
		if doc.docstatus == 0:
			return doc
		elif doc.docstatus == 1:
			frappe.msgprint(_("Result already Submitted"))
			return None
	else:
		return frappe.new_doc("Assessment Result")


@frappe.whitelist()
def update_email_group(doctype, name):
	if not frappe.db.exists("Email Group", name):
		email_group = frappe.new_doc("Email Group")
		email_group.title = name
		email_group.save()
	email_list = []
	students = []
	if doctype == "Student Group":
		students = get_student_group_students(name)
	for stud in students:
		for guard in get_student_guardians(stud.student):
			email = frappe.db.get_value("Guardian", guard.guardian, "email_address")
			if email:
				email_list.append(email)
	add_subscribers(name, email_list)


@frappe.whitelist()
def get_current_enrollment(student, academic_year=None):
	"""Get all active program enrollments for a student.
	
	Returns all enrollments where academic year hasn't ended yet.
	
	:param student: Student name/ID
	:param academic_year: Optional date to compare (defaults to today)
	:return: List of active program enrollments (or None if empty)
	"""
	# If academic_year is not passed, use today's date
	compare_date = getdate(academic_year) if academic_year else getdate(today())

	program_enrollment_list = frappe.db.sql(
		"""
		SELECT
			pe.name AS program_enrollment, pe.student_name, pe.program, pe.student_batch_name AS student_batch,
			pe.student_category, pe.academic_term, pe.academic_year
		FROM
			`tabProgram Enrollment` pe
		JOIN
			`tabAcademic Year` ay ON pe.academic_year = ay.name
		WHERE
			pe.student = %s
			AND ay.year_end_date >= %s
		ORDER BY
			pe.creation DESC
		""",
		(student, compare_date),
		as_dict=1,
	)

	if program_enrollment_list:
		return program_enrollment_list  # Return ALL active enrollments
	else:
		return None


@frappe.whitelist()
def get_instructors(student_group):
	return frappe.get_all(
		"Student Group Instructor", {"parent": student_group}, pluck="instructor"
	)


@frappe.whitelist()
def get_course_schedule_student_group_defaults(student_group):
	"""Return Student Group defaults used by the Course Schedule form."""
	if not student_group:
		return {}

	doc = frappe.get_doc("Student Group", student_group)
	if not doc.has_permission("read"):
		frappe.throw(_("Not permitted to read this student group"), frappe.PermissionError)

	start_date = doc.start_date
	end_date = doc.end_date

	instructors = [row.instructor for row in doc.instructors if row.instructor]
	return {
		"program": doc.program,
		"course": doc.course,
		"start_date": start_date,
		"end_date": end_date,
		"instructors": instructors,
	}


@frappe.whitelist()
def get_user_info():
	if frappe.session.user == "Guest":
		frappe.throw("Authentication failed", exc=frappe.AuthenticationError)

	current_user = frappe.db.get_list(
		"User",
		fields=["name", "email", "enabled", "user_image", "full_name", "user_type"],
		filters={"name": frappe.session.user},
	)[0]
	current_user["session_user"] = True
	return current_user


@frappe.whitelist()
def get_student_info():
	email = frappe.session.user
	if email == "Administrator":
		return
	student_info = frappe.db.get_list(
		"Student",
		fields=["*"],
		filters={"user": email},
	)[0]

	current_programs = get_current_enrollment(student_info.name)
	if current_programs:
		# Collect student groups from ALL active programs
		all_student_groups = []
		for program in current_programs:
			groups = get_student_groups(student_info.name, program.program)
			all_student_groups.extend(groups)
		
		# Remove duplicates (in case student is in same group via multiple programs)
		seen = set()
		unique_groups = []
		for g in all_student_groups:
			if g.label not in seen:
				seen.add(g.label)
				unique_groups.append(g)
		
		student_info["student_groups"] = unique_groups
		student_info["current_programs"] = current_programs  # List of all programs
		student_info["current_program"] = current_programs[0]  # Keep backward compatibility (newest)
	return student_info


@frappe.whitelist()
def get_student_programs(student):
	# student = 'EDU-STU-2023-00043'
	programs = frappe.db.get_list(
		"Program Enrollment",
		fields=["program", "name"],
		filters={"docstatus": 1, "student": student},
	)
	return programs


def get_student_groups(student, program_name):
	# student = 'EDU-STU-2023-00043'

	student_group = frappe.qb.DocType("Student Group")
	student_group_students = frappe.qb.DocType("Student Group Student")

	student_group_query = (
		frappe.qb.from_(student_group)
		.inner_join(student_group_students)
		.on(student_group.name == student_group_students.parent)
		.select((student_group_students.parent).as_("label"))
		.distinct()
		.where(student_group_students.student == student)
		.where(student_group.program == program_name)
		.run(as_dict=1)
	)

	return student_group_query


@frappe.whitelist()
def get_all_student_groups(student):
	"""Return all student groups of a given student (across all programs).

	:param student: Student name (ID)
	"""
	student_group = frappe.qb.DocType("Student Group")
	student_group_students = frappe.qb.DocType("Student Group Student")

	student_group_query = (
		frappe.qb.from_(student_group)
		.inner_join(student_group_students)
		.on(student_group.name == student_group_students.parent)
		.select(
			student_group.name.as_("name"),
			student_group.student_group_name.as_("student_group_name"),
			student_group.program.as_("program"),
			student_group.course.as_("course"),
		)
		.where(student_group_students.student == student)
		.orderby(student_group.program)
		.run(as_dict=1)
	)

	# Attach full student info list for each student group
	for row in student_group_query:
		row["students"] = get_student_group_students_full(row["name"])

	return student_group_query


def get_student_group_students_full(student_group_name):
	"""Return minimal Student info (name, student_name, image, custom_total_badge_point)
	for all students in a given student group, sorted by custom_total_badge_point desc.
	
	NOTE: This returns total badge points across ALL groups (from Student.custom_total_badge_point).
	For badge points specific to a group, use get_student_group_students_with_group_badge_points().
	"""
	students_in_group = frappe.get_all(
		"Student Group Student",
		fields=["student"],
		filters={"parent": student_group_name},
	)

	student_ids = [s.student for s in students_in_group if s.student]
	if not student_ids:
		return []

	students = frappe.get_all(
		"Student",
		fields=["name", "student_name", "image", "custom_total_badge_point"],
		filters={"name": ["in", student_ids]},
	)

	# Sort in Python to be safe if field is nullable / string
	students.sort(
		key=lambda s: float(s.get("custom_total_badge_point") or 0),
		reverse=True,
	)

	return students


def get_student_group_students_with_group_badge_points(student_group_name):
	"""Return Student info with badge points calculated for THIS GROUP ONLY.
	
	Calculates badge points by summing badge_points from Student Badge child table
	where student_group matches the given group.
	
	OPTIMIZED: Uses single SQL query with JOIN instead of N queries.
	
	:param student_group_name: Student Group name
	:return: List of students with group_badge_points (sorted desc)
	"""
	# Single optimized query: JOIN students with their badge points for this group
	students = frappe.db.sql(
		"""
		SELECT 
			s.name,
			s.student_name,
			s.image,
			COALESCE(SUM(CAST(sb.badge_points AS DECIMAL(10,2))), 0) as group_badge_points
		FROM `tabStudent Group Student` sgs
		INNER JOIN `tabStudent` s ON s.name = sgs.student
		LEFT JOIN `tabStudent Badge` sb ON sb.parent = s.name AND sb.student_group = %s
		WHERE sgs.parent = %s
		GROUP BY s.name, s.student_name, s.image
		ORDER BY group_badge_points DESC
		""",
		(student_group_name, student_group_name),
		as_dict=True
	)

	# Convert Decimal to float for JSON serialization
	for student in students:
		student["group_badge_points"] = float(student.get("group_badge_points") or 0)

	return students


@frappe.whitelist()
def get_all_student_groups_with_badge_points(student):
	"""Return all student groups of a given student with badge points calculated PER GROUP.
	
	Unlike get_all_student_groups() which uses custom_total_badge_point (total of ALL badges),
	this API calculates badge points for each group by summing from Student Badge child table.
	
	:param student: Student name (ID)
	:return: List of student groups with students and their group-specific badge points
	"""
	student_group = frappe.qb.DocType("Student Group")
	student_group_students = frappe.qb.DocType("Student Group Student")

	student_group_query = (
		frappe.qb.from_(student_group)
		.inner_join(student_group_students)
		.on(student_group.name == student_group_students.parent)
		.select(
			student_group.name.as_("name"),
			student_group.student_group_name.as_("student_group_name"),
			student_group.program.as_("program"),
			student_group.course.as_("course"),
		)
		.where(student_group_students.student == student)
		.orderby(student_group.program)
		.run(as_dict=1)
	)

	# Attach student info with GROUP-SPECIFIC badge points
	for row in student_group_query:
		row["students"] = get_student_group_students_with_group_badge_points(row["name"])

	return student_group_query


@frappe.whitelist()
def get_student_badges_in_group(student, student_group):
	"""Return all badges of a student in a specific student group.
	
	:param student: Student name (ID)
	:param student_group: Student Group name
	:return: List of badges with full details (badge_name, badge_points, badge_level, etc.)
	"""
	if not student:
		frappe.throw(_("Missing student name"))
	if not student_group:
		frappe.throw(_("Missing student_group name"))

	# Query badges from Student Badge child table
	badges = frappe.db.sql(
		"""
		SELECT 
			sb.name,
			sb.badge,
			sb.badge_name,
			sb.badge_points,
			sb.badge_level,
			sb.badge_description,
			sb.badge_criteria,
			sb.badge_link_image,
			sb.student_group
		FROM `tabStudent Badge` sb
		WHERE sb.parent = %s AND sb.student_group = %s
		ORDER BY sb.badge_points DESC
		""",
		(student, student_group),
		as_dict=True
	)

	# Convert badge_points to float for JSON serialization
	for badge in badges:
		badge["badge_points"] = float(badge.get("badge_points") or 0)

	return badges


@frappe.whitelist()
def get_course_list_based_on_program(program_name, program_enrollment=None, student=None):
	if program_enrollment:
		enrollment_doc = frappe.get_doc("Program Enrollment", program_enrollment)

		if program_name and enrollment_doc.program != program_name:
			frappe.throw(_("Program mismatch for the requested enrollment."))

		if student and enrollment_doc.student != student:
			frappe.throw(_("Student mismatch for the requested enrollment."))

		return [course.course for course in enrollment_doc.courses if course.course]

	courses = get_course(program_name)
	return [course.get("course") for course in courses if course.get("course")]


@frappe.whitelist()
def get_course_schedule_for_student(program_name, student_groups):
	student_groups = [sg.get("label") for sg in student_groups]

	schedule = frappe.db.get_list(
		"Course Schedule",
		fields=[
			"schedule_date",
			"room",
			"class_schedule_color",
			"course",
			"from_time",
			"to_time",
			"instructor",
			"title",
			"name",
		],
		filters={"program": program_name, "student_group": ["in", student_groups]},
		order_by="schedule_date asc",
	)
	
	# Map room ID to room_name
	for item in schedule:
		if item.get("room"):
			room_name = frappe.db.get_value("Room", item["room"], "room_name")
			item["room_name"] = room_name or item["room"]
		else:
			item["room_name"] = None
	
	return schedule


@frappe.whitelist()
def apply_leave(leave_data, program_name, student_group=None):
	"""Apply leave for a student.
	
	:param leave_data: Leave data (student, from_date, to_date, reason, etc.)
	:param program_name: Program name
	:param student_group: Specific student group to apply leave for (optional)
	                      If provided, only creates leave for this group.
	                      If not provided, creates leave for all groups in program.
	"""
	attendance_based_on_course_schedule = frappe.db.get_single_value(
		"Education Settings", "attendance_based_on_course_schedule"
	)
	if attendance_based_on_course_schedule:
		apply_leave_based_on_course_schedule(leave_data, program_name)
	else:
		apply_leave_based_on_student_group(leave_data, program_name, student_group)


def apply_leave_based_on_course_schedule(leave_data, program_name):
	course_schedule_in_leave_period = frappe.db.get_list(
		"Course Schedule",
		fields=["name", "schedule_date"],
		filters={
			"program": program_name,
			"schedule_date": [
				"between",
				[leave_data.get("from_date"), leave_data.get("to_date")],
			],
		},
		order_by="schedule_date asc",
	)
	if not course_schedule_in_leave_period:
		frappe.throw(_("Không tìm thấy lớp học trong khoảng thời gian nghỉ"))
	
	created_count = 0
	# Create Student Leave Application for each course schedule
	for course_schedule in course_schedule_in_leave_period:
		# Check if attendance record already exists for the student on the course schedule
		existing_attendance = frappe.db.exists(
			"Student Attendance",
			{"course_schedule": course_schedule.get("name"), "student": leave_data.get("student"), "docstatus": ("!=", 2)},
		)
		if existing_attendance:
			continue  # Skip if attendance already exists
		
		# Check if leave application already exists
		existing_leave = frappe.db.exists(
			"Student Leave Application",
			{
				"student": leave_data.get("student"),
				"course_schedule": course_schedule.get("name"),
				"docstatus": ("!=", 2),
			},
		)
		if existing_leave:
			continue  # Skip if leave application already exists
		
		# Create Student Leave Application
		# Note: on_submit() of Student Leave Application will automatically create Student Attendance
		leave_application = frappe.new_doc("Student Leave Application")
		leave_application.student = leave_data.get("student")
		leave_application.student_name = leave_data.get("student_name")
		leave_application.from_date = course_schedule.get("schedule_date")
		leave_application.to_date = course_schedule.get("schedule_date")
		leave_application.reason = leave_data.get("reason")
		leave_application.attendance_based_on = "Course Schedule"
		leave_application.course_schedule = course_schedule.get("name")
		leave_application.total_leave_days = 1
		leave_application.flags.ignore_permissions = True
		leave_application.save()
		leave_application.submit()
		created_count += 1
	
	if created_count == 0:
		frappe.throw(_("Bạn đã đăng ký nghỉ phép cho tất cả các lớp trong ngày này rồi"))


def apply_leave_based_on_student_group(leave_data, program_name, student_group=None):
	"""Apply leave based on student group.
	
	:param leave_data: Leave data
	:param program_name: Program name
	:param student_group: Specific student group (if provided, only apply for this group)
	"""
	# If specific student_group is provided, use only that group
	# Otherwise, get all groups for the student in this program
	if student_group:
		student_groups = [{"label": student_group}]
	else:
		student_groups = get_student_groups(leave_data.get("student"), program_name)
	
	if not student_groups:
		frappe.throw(_("Không tìm thấy lớp học nào cho học sinh này"))
	
	leave_dates = get_dates_from_timegrain(
		leave_data.get("from_date"), leave_data.get("to_date")
	)
	
	# Check if attendance already exists for any of the leave dates (before creating anything)
	for sg in student_groups:
		for leave_date in leave_dates:
			existing_attendance = frappe.db.exists(
				"Student Attendance",
				{
					"student": leave_data.get("student"),
					"student_group": sg.get("label"),
					"date": leave_date,
					"docstatus": ("!=", 2),  # Not cancelled
				},
			)
			if existing_attendance:
				frappe.throw(_("Đã có bản ghi điểm danh cho ngày {0} trong lớp {1}").format(leave_date, sg.get("label")))
	
	# Create Student Leave Application for each student group
	for sg in student_groups:
		# Check if leave application already exists for this student, student_group and date range
		existing_leave = frappe.db.exists(
			"Student Leave Application",
			{
				"student": leave_data.get("student"),
				"student_group": sg.get("label"),
				"from_date": leave_data.get("from_date"),
				"to_date": leave_data.get("to_date"),
				"docstatus": ("!=", 2),  # Not cancelled
			},
		)
		if existing_leave:
			frappe.throw(_("Bạn đã đăng ký nghỉ phép cho lớp {0} trong ngày này rồi").format(sg.get("label")))
		
		# Create Student Leave Application
		# Note: on_submit() of Student Leave Application will automatically create Student Attendance
		leave_application = frappe.new_doc("Student Leave Application")
		leave_application.student = leave_data.get("student")
		leave_application.student_name = leave_data.get("student_name")
		leave_application.from_date = leave_data.get("from_date")
		leave_application.to_date = leave_data.get("to_date")
		leave_application.reason = leave_data.get("reason")
		leave_application.attendance_based_on = "Student Group"
		leave_application.student_group = sg.get("label")
		leave_application.total_leave_days = len(leave_dates)
		leave_application.flags.ignore_permissions = True
		leave_application.save()
		leave_application.submit()


@frappe.whitelist()
def get_student_invoices(student):
	student_sales_invoices = []

	sales_invoice_list = frappe.db.get_list(
		"Sales Invoice",
		filters={
			"student": student,
			"status": ["in", ["Paid", "Unpaid", "Overdue", "Partly Paid"]],
			"docstatus": 1,
		},
		fields=[
			"name",
			"status",
			"student",
			"due_date",
			"fee_schedule",
			"outstanding_amount",
			"currency",
			"grand_total",
		],
		order_by="status desc",
	)

	for si in sales_invoice_list:
		student_program_invoice_status = {}
		student_program_invoice_status["status"] = si.status
		student_program_invoice_status["program"] = get_program_from_fee_schedule(
			si.fee_schedule
		)
		symbol = get_currency_symbol(si.get("currency", "INR"))
		student_program_invoice_status["amount"] = symbol + " " + str(si.outstanding_amount)
		student_program_invoice_status["invoice"] = si.name
		if si.status == "Paid":
			student_program_invoice_status["amount"] = symbol + " " + str(si.grand_total)
			student_program_invoice_status[
				"payment_date"
			] = get_posting_date_from_payment_entry_against_sales_invoice(si.name)
			student_program_invoice_status["due_date"] = "-"
		else:
			student_program_invoice_status["due_date"] = si.due_date
			student_program_invoice_status["payment_date"] = "-"

		student_sales_invoices.append(student_program_invoice_status)

	print_format = get_fees_print_format() or "Standard"

	return {"invoices": student_sales_invoices, "print_format": print_format}


def get_currency_symbol(currency):
	return frappe.db.get_value("Currency", currency, "symbol") or currency


def get_posting_date_from_payment_entry_against_sales_invoice(sales_invoice):
	payment_entry = frappe.qb.DocType("Payment Entry")
	payment_entry_reference = frappe.qb.DocType("Payment Entry Reference")

	q = (
		frappe.qb.from_(payment_entry)
		.inner_join(payment_entry_reference)
		.on(payment_entry.name == payment_entry_reference.parent)
		.select(payment_entry.posting_date)
		.where(payment_entry_reference.reference_name == sales_invoice)
	).run(as_dict=1)

	if len(q) > 0:
		payment_date = q[0].get("posting_date")
		return payment_date


def get_fees_print_format():
	return frappe.db.get_value(
		"Property Setter",
		dict(property="default_print_format", doc_type="Sales Invoice"),
		"value",
	)


def get_program_from_fee_schedule(fee_schedule):

	program = frappe.db.get_value(
		"Fee Schedule", filters={"name": fee_schedule}, fieldname=["program"]
	)
	return program


@frappe.whitelist()
def get_school_abbr_logo():
	abbr = frappe.db.get_single_value(
		"Education Settings", "school_college_name_abbreviation"
	)
	logo = frappe.db.get_single_value("Education Settings", "school_college_logo")
	return {"name": abbr, "logo": logo}


@frappe.whitelist()
def get_student_attendance(student, student_group):
	return frappe.db.get_list(
		"Student Attendance",
		filters={"student": student, "student_group": student_group, "docstatus": 1},
		fields=["date", "status", "name"],
	)


@frappe.whitelist()
def get_student_groups_for_attendance(student):
	"""Get all student groups that a student belongs to, with program info.
	
	Returns list of student groups with program name for attendance filtering.
	"""
	student_group = frappe.qb.DocType("Student Group")
	student_group_student = frappe.qb.DocType("Student Group Student")
	
	result = (
		frappe.qb.from_(student_group)
		.inner_join(student_group_student)
		.on(student_group.name == student_group_student.parent)
		.select(
			student_group.name.as_("value"),
			student_group.student_group_name.as_("label"),
			student_group.program.as_("program"),
		)
		.where(student_group_student.student == student)
		.where(student_group.disabled == 0)
		.orderby(student_group.program)
		.orderby(student_group.student_group_name)
		.run(as_dict=True)
	)
	
	return result


@frappe.whitelist()
def get_student_groups_for_student(student):
	"""Get all student groups that a student belongs to.
	
	Used in Student form to populate Group name select field.
	Returns list of group names.
	
	:param student: Student name/ID
	"""
	if not student:
		return []
	
	groups = frappe.get_all(
		"Student Group Student",
		filters={"student": student},
		fields=["parent"],
		distinct=True,
	)
	
	return [g.parent for g in groups]


@frappe.whitelist()
def get_student_groups_for_link(doctype, txt, searchfield, start, page_len, filters):
	"""Get student groups for Link field query.
	
	Used in Student form for custom_group_name Link field.
	Only returns groups that the student belongs to.
	"""
	student = filters.get("student")
	if not student:
		return []
	
	groups = frappe.get_all(
		"Student Group Student",
		filters={"student": student},
		fields=["parent"],
		distinct=True,
	)
	
	group_names = [g.parent for g in groups]
	
	if not group_names:
		return []
	
	# Filter by search text if provided
	if txt:
		group_names = [g for g in group_names if txt.lower() in g.lower()]
	
	return [[g] for g in group_names[start:start + page_len]]


# Homework

@frappe.whitelist()
def submit_homework(
	homework_name=None,
	student=None,
	description=None,
	file=None,
	link_file=None,
	parent=None,
	parentfield="list_student_submit",
	parenttype="Homework",
):
	"""Submit homework for a student by creating a Student Homework record.

	You can truyền cả thông tin parent:
	- parent: tên Homework (ví dụ: Homework-420-18-12-2025)
	- parentfield: phải là 'list_student_submit'
	- parenttype: phải là 'Homework'

	:param homework_name: Name of the Homework document (có thể bỏ nếu đã truyền parent)
	:param parent: Parent name (Homework name)
	:param parentfield: Child table fieldname on Homework (mặc định: list_student_submit)
	:param parenttype: Parent doctype (mặc định: Homework)
	:param student: Student ID
	:param description: Optional description of the submission
	:param file: Optional file attachment (đường dẫn file trong File doctype)
	:param link_file: Optional link to file
	"""
	# Validate student trước
	if not student:
		frappe.throw(_("Thiếu thông tin học sinh. Vui lòng cung cấp student name."))

	# Ưu tiên dùng parent nếu được truyền vào
	homework_id = parent or homework_name
	if not homework_id:
		frappe.throw(_("Thiếu tên bài tập về nhà. Vui lòng cung cấp homework_name hoặc parent."))

	# Validate parent info nếu có truyền vào
	if parenttype and parenttype != "Homework":
		frappe.throw(_("parenttype không hợp lệ. Phải là 'Homework', nhận được: {0}").format(parenttype))
	if parentfield and parentfield != "list_student_submit":
		frappe.throw(_("parentfield không hợp lệ. Phải là 'list_student_submit', nhận được: {0}").format(parentfield))

	# Get the homework document
	try:
		homework_doc = frappe.get_doc("Homework", homework_id)
	except frappe.DoesNotExistError:
		frappe.throw(_("Không tìm thấy bài tập về nhà với tên: {0}").format(homework_id))
	except Exception as e:
		frappe.throw(_("Lỗi khi tải bài tập về nhà: {0}").format(str(e)))

	# Check if student already submitted (đảm bảo mỗi student chỉ có 1 submission cho mỗi homework)
	existing_submission = None
	for submission in homework_doc.list_student_submit:
		if submission.student == student:
			existing_submission = submission
			break

	# Double check từ database để đảm bảo không có duplicate
	if not existing_submission:
		existing_db_submission = frappe.db.exists(
			"Student Homework",
			{"parent": homework_id, "student": student}
		)
		if existing_db_submission:
			# Nếu có trong DB nhưng chưa load vào doc, reload doc
			homework_doc.reload()
			for submission in homework_doc.list_student_submit:
				if submission.student == student:
					existing_submission = submission
					break

	if existing_submission:
		# Update existing submission
		try:
			existing_submission.description = description
			existing_submission.file = file
			existing_submission.link_file = link_file
			homework_doc.save()
			frappe.db.commit()
			return {
				"success": True,
				"message": _("Cập nhật bài nộp thành công."),
				"submission": existing_submission.as_dict(),
			}
		except Exception as e:
			frappe.db.rollback()
			frappe.throw(_("Lỗi khi cập nhật bài nộp: {0}").format(str(e)))
	else:
		# Create new submission (Frappe sẽ tự set parent/parentfield/parenttype đúng)
		try:
			homework_doc.append(
				"list_student_submit",
				{
					"student": student,
					"description": description,
					"file": file,
					"link_file": link_file,
					"score": None,
					"comment": None,
				},
			)
			homework_doc.save()
			frappe.db.commit()

			# Get the newly created submission
			new_submission = homework_doc.list_student_submit[-1]

			return {
				"success": True,
				"message": _("Nộp bài tập thành công."),
				"submission": new_submission.as_dict(),
			}
		except Exception as e:
			frappe.db.rollback()
			frappe.throw(_("Lỗi khi nộp bài tập: {0}").format(str(e)))


@frappe.whitelist()
def get_homework(homework_name):
	"""Lấy đầy đủ thông tin của một Homework (KHÔNG bao gồm child table list_student_submit)."""
	if not homework_name:
		frappe.throw(_("Missing Homework name"))

	doc = frappe.get_doc("Homework", homework_name)

	# Lấy dict đầy đủ rồi loại bỏ trường list_student_submit
	data = doc.as_dict()
	data.pop("list_student_submit", None)
	return data


@frappe.whitelist()
def get_homeworks(homework_names):
	"""Lấy danh sách Homework theo mảng tên truyền vào (KHÔNG bao gồm list_student_submit).

	- homework_names: có thể truyền dạng list (JS) hoặc JSON string (REST)
	"""
	if not homework_names:
		frappe.throw(_("Missing homework_names"))

	# Cho phép gọi từ JS (truyền list) hoặc REST (truyền JSON string)
	if isinstance(homework_names, str):
		try:
			homework_names = json.loads(homework_names)
		except Exception:
			frappe.throw(_("Invalid homework_names format, must be JSON array or list"))

	if not isinstance(homework_names, (list, tuple)):
		frappe.throw(_("homework_names must be a list"))

	homework_names = [n for n in homework_names if n]
	if not homework_names:
		return []

	docs = []
	for name in homework_names:
		try:
			doc = frappe.get_doc("Homework", name)
			data = doc.as_dict()
			data.pop("list_student_submit", None)
			docs.append(data)
		except frappe.DoesNotExistError:
			# Bỏ qua nếu không tồn tại, hoặc có thể push lỗi tùy nhu cầu
			continue

	return docs


@frappe.whitelist()
def get_homeworks_by_student(student):
	"""Lấy tất cả Homework được giao cho student dựa trên các chương trình học,
	các khóa học, các Topic và lớp học (Student Group) mà student đang học.

	Logic:
	- Lấy tất cả Program Enrollment (đã submit) của student
	- Lấy tất cả Student Groups mà student thuộc về
	- Từ mỗi Program, lấy danh sách Course (Program Course)
	- Từ mỗi Course, lấy danh sách Topic (Course Topic)
	- Từ mỗi Topic, đọc child table custom_homework (Topic Homework) để lấy danh sách Homework được giao
	- Lọc Homework theo student_group:
	  + Homework có student_group khớp với các groups của student
	  + Hoặc Homework không có student_group (giao cho tất cả)
	- Tổng hợp danh sách Homework (unique) và trả về chi tiết từng Homework

	:param student: Student name/ID
	:return: Danh sách Homework (BAO GỒM list_student_submit)
	"""
	if not student:
		frappe.throw(_("Missing student name"))

	# Lấy các Program Enrollment của student
	program_enrollments = frappe.get_all(
		"Program Enrollment",
		filters={"student": student, "docstatus": 1},
		fields=["program"],
	)

	if not program_enrollments:
		return []

	# Lấy tất cả Student Groups mà student thuộc về
	student_groups = frappe.get_all(
		"Student Group Student",
		filters={"student": student},
		fields=["parent"],
		distinct=True,
	)
	student_group_names = [sg.parent for sg in student_groups]

	homework_names = set()
	# Map homework_name -> danh sách bối cảnh giao bài (program / course / topic / topic_homework)
	homework_context_map = {}

	for pe in program_enrollments:
		program_name = pe.get("program")
		if not program_name:
			continue

		# Lấy Program và các Course của Program
		program_doc = frappe.get_doc("Program", program_name)
		for program_course in getattr(program_doc, "courses", []):
			course_name = getattr(program_course, "course", None)
			if not course_name:
				continue

			# Lấy Course và các Topic của Course
			course_doc = frappe.get_doc("Course", course_name)
			for course_topic in getattr(course_doc, "topics", []):
				topic_name = getattr(course_topic, "topic", None)
				if not topic_name:
					continue

				# Lấy Topic và danh sách Homework được gán qua custom_homework (Topic Homework)
				topic_doc = frappe.get_doc("Topic", topic_name)
				for th in getattr(topic_doc, "custom_homework", []):
					hw = getattr(th, "homework", None)
					if not hw:
						continue

					homework_names.add(hw)

					# Lưu lại bối cảnh (program / course / topic) mà homework này được giao
					context_list = homework_context_map.setdefault(hw, [])
					context_list.append(
						{
							"program": program_name,
							"course": course_name,
							"topic": topic_name,
							"topic_homework": getattr(th, "name", None),
							"homework_title": getattr(th, "homework_title", None),
						}
					)

	if not homework_names:
		return []

	# Lấy chi tiết từng Homework:
	# - Lọc theo student_group (chỉ lấy homework của lớp mình hoặc không có lớp)
	# - BẢO GỒM list_student_submit nhưng CHỈ của chính student hiện tại
	# - Gắn thêm thông tin bối cảnh (program / course / topic)
	docs = []
	for name in homework_names:
		try:
			doc = frappe.get_doc("Homework", name)

			# Lọc theo student_group:
			# - Nếu homework có student_group, chỉ lấy nếu student thuộc group đó
			# - Nếu homework không có student_group (None hoặc ""), lấy cho tất cả
			hw_student_group = doc.get("student_group")
			if hw_student_group and hw_student_group not in student_group_names:
				# Homework này được giao cho lớp khác, bỏ qua
				continue

			# Bản đầy đủ để không mất field nào
			data = doc.as_dict()

			# Chỉ giữ lại các dòng list_student_submit thuộc về student hiện tại
			submissions = [
				row.as_dict()
				for row in (doc.get("list_student_submit") or [])
				if getattr(row, "student", None) == student
			]
			data["list_student_submit"] = submissions

			# Gắn thêm thông tin bối cảnh (program / course / topic) nơi homework được giao
			data["assigned_in"] = homework_context_map.get(name, [])

			docs.append(data)
		except frappe.DoesNotExistError:
			continue

	return docs


@frappe.whitelist()
def get_student_homework_submission(homework_name, student):
	"""Lấy submission của student cho một homework cụ thể.
	
	:param homework_name: Homework name
	:param student: Student name/ID
	:return: Student Homework submission hoặc None nếu chưa nộp
	"""
	if not homework_name:
		frappe.throw(_("Missing homework_name"))
	if not student:
		frappe.throw(_("Missing student name"))

	# Query từ Student Homework table
	submission = frappe.get_all(
		"Student Homework",
		filters={"parent": homework_name, "student": student},
		fields=["*"],
		limit=1,
	)

	if submission:
		return submission[0]
	else:
		return None


@frappe.whitelist()
def upload_education_file():
	"""Upload file (multipart/form-data) và lưu vào File doctype.

	Chấp nhận cùng định dạng form như frontend `uploadFile` (useApi.js):
	- file: file content (bắt buộc)
	- file_name / filename: tên file (tuỳ chọn, fallback từ file.filename)
	- is_private: '1' hoặc '0' (mặc định: 1)
	- folder: thư mục (mặc định: 'Home')
	- doctype, docname, fieldname: nếu cần đính kèm vào document
	"""
	file = frappe.request.files.get("file")
	if not file:
		frappe.throw(_("Thiếu file upload. Vui lòng chọn file."))

	filename = frappe.form_dict.get("file_name") or frappe.form_dict.get("filename") or file.filename
	if not filename:
		frappe.throw(_("Không xác định được tên file."))

	# Đọc nội dung file
	content = file.stream.read()
	if content is None:
		frappe.throw(_("Không thể đọc nội dung file."))

	# Luôn lưu public
	is_private = 0
	folder = frappe.form_dict.get("folder") or "Home"
	doctype = frappe.form_dict.get("doctype")
	docname = frappe.form_dict.get("docname")
	fieldname = frappe.form_dict.get("fieldname")

	try:
		# API save_file hiện nhận dạng: save_file(fname, content, dt=None, dn=None, folder=None, is_private=0)
		file_doc = save_file(
			filename,
			content,
			doctype,
			docname,
			folder=folder,
			is_private=is_private,
		)

		return {
			"success": True,
			"name": file_doc.name,
			"file_url": file_doc.file_url,
			"file_name": file_doc.file_name,
			"is_private": file_doc.is_private,
			"folder": file_doc.folder,
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Education Upload File Failed")
		frappe.throw(_("Lỗi khi upload file: {0}").format(str(e)))


@frappe.whitelist()
def get_assessment_result_detail(result_name):
	"""Returns detailed Assessment Result with criteria details and comments
	
	:param result_name: Assessment Result name
	"""
	# Get main assessment result
	result = frappe.get_doc("Assessment Result", result_name)
	
	if not result:
		frappe.throw(_("Assessment Result not found"))
	
	# Get assessment result details (criteria)
	details = frappe.get_all(
		"Assessment Result Detail",
		fields=[
			"name",
			"assessment_criteria",
			"maximum_score",
			"score",
			"grade",
			"idx"
		],
		filters={"parent": result_name},
		order_by="idx"
	)
	
	# Get commenter info (modified_by is the last person who edited)
	comment_by = None
	comment_by_name = None
	if result.comment:
		# Get full name of the person who last modified
		comment_by = result.modified_by or result.owner
		if comment_by:
			comment_by_name = frappe.db.get_value("User", comment_by, "full_name") or comment_by
	
	return {
		"name": result.name,
		"student": result.student,
		"student_name": result.student_name,
		"assessment_group": result.assessment_group,
		"student_group": result.student_group,
		"course": result.course,
		"grading_scale": result.grading_scale,
		"creation": result.creation,
		"modified": result.modified,
		"total_score": result.total_score,
		"maximum_score": result.maximum_score,
		"grade": result.grade,
		"comment": result.comment,
		"comment_by": comment_by_name,
		"docstatus": result.docstatus,
		"details": details
	}


@frappe.whitelist()
def get_topics_by_course(doctype, txt, searchfield, start, page_len, filters):
	"""Get topics that belong to a specific course.
	
	Used in Homework form for linked_topic Link field.
	Only returns topics that belong to the selected course via Course Topic child table.
	
	:param filters: Must contain 'course' key
	"""
	course = filters.get("course")
	if not course:
		# If no course filter, return all topics
		return frappe.db.sql(
			"""
			SELECT name, topic_name
			FROM `tabTopic`
			WHERE (name LIKE %(txt)s OR topic_name LIKE %(txt)s)
			ORDER BY topic_name
			LIMIT %(start)s, %(page_len)s
			""",
			{
				"txt": f"%{txt}%",
				"start": start,
				"page_len": page_len,
			}
		)
	
	# Get topics that belong to this course via Course Topic child table
	return frappe.db.sql(
		"""
		SELECT t.name, t.topic_name
		FROM `tabTopic` t
		INNER JOIN `tabCourse Topic` ct ON ct.topic = t.name
		WHERE ct.parent = %(course)s
			AND (t.name LIKE %(txt)s OR t.topic_name LIKE %(txt)s)
		ORDER BY ct.idx, t.topic_name
		LIMIT %(start)s, %(page_len)s
		""",
		{
			"course": course,
			"txt": f"%{txt}%",
			"start": start,
			"page_len": page_len,
		}
	)


@frappe.whitelist()
def get_available_course_schedule_topics(doctype, txt, searchfield, start, page_len, filters):
	"""Get course topics that are not already assigned to another Course Schedule."""
	filters = filters or {}
	course = filters.get("course")
	course_schedule = filters.get("course_schedule")
	if not course:
		return []

	return frappe.db.sql(
		"""
		SELECT t.name, t.topic_name
		FROM `tabTopic` t
		INNER JOIN `tabCourse Topic` ct ON ct.topic = t.name
		WHERE ct.parent = %(course)s
			AND (t.name LIKE %(txt)s OR t.topic_name LIKE %(txt)s)
			AND NOT EXISTS (
				SELECT 1
				FROM `tabCourse Schedule` cs
				WHERE cs.course = %(course)s
					AND cs.topic = t.name
					AND cs.docstatus != 2
					AND (%(course_schedule)s IS NULL OR %(course_schedule)s = '' OR cs.name != %(course_schedule)s)
			)
		ORDER BY ct.idx, t.topic_name
		LIMIT %(start)s, %(page_len)s
		""",
		{
			"course": course,
			"course_schedule": course_schedule,
			"txt": f"%{txt}%",
			"start": start,
			"page_len": page_len,
		},
	)


@frappe.whitelist()
def get_course_topics(course):
	"""Get list of topic names that belong to a course.
	
	:param course: Course name
	:return: List of topic names
	"""
	if not course:
		return []
	
	topics = frappe.db.get_all(
		'Course Topic',
		filters={'parent': course},
		fields=['topic'],
		order_by='idx'
	)
	
	return [t.topic for t in topics if t.topic]


def _attendance_date(value, fieldname="date"):
	if not value:
		frappe.throw(_("{0} is required").format(_(fieldname.replace("_", " ").title())))
	return getdate(value)


def _attendance_statuses():
	meta = frappe.get_meta("Student Attendance")
	status_field = meta.get_field("status")
	options = [cstr(status).strip() for status in (status_field.options or "").split("\n")]
	return [status for status in options if status]


def _validate_attendance_status(status):
	status = cstr(status).strip()
	if not status:
		return ""
	if status not in _attendance_statuses():
		frappe.throw(_("Invalid attendance status {0}").format(frappe.bold(status)))
	return status


def _ensure_attendance_read_permission():
	if not frappe.has_permission("Student Attendance", "read"):
		frappe.throw(_("Not permitted to read student attendance"), frappe.PermissionError)


def _ensure_student_group_read_permission(student_group):
	if not student_group:
		frappe.throw(_("Student Group is required"))
	doc = frappe.get_doc("Student Group", student_group)
	if not doc.has_permission("read"):
		frappe.throw(_("Not permitted to read Student Group {0}").format(student_group), frappe.PermissionError)
	return doc


def _ensure_student_read_permission(student):
	if not student:
		frappe.throw(_("Student is required"))
	doc = frappe.get_doc("Student", student)
	if not doc.has_permission("read"):
		frappe.throw(_("Not permitted to read Student {0}").format(student), frappe.PermissionError)
	return doc


def _student_belongs_to_group(student, student_group):
	return frappe.db.exists(
		"Student Group Student",
		{"parent": student_group, "student": student, "active": 1},
	)


def _get_group_students(student_group):
	_ensure_student_group_read_permission(student_group)
	return frappe.get_all(
		"Student Group Student",
		fields=["student", "student_name", "group_roll_number"],
		filters={"parent": student_group, "active": 1},
		order_by="group_roll_number asc, student_name asc",
	)


def _attendance_summary(rows):
	statuses = _attendance_statuses()
	counts = {status: 0 for status in statuses}
	for row in rows:
		status = row.get("status")
		if status:
			counts[status] = counts.get(status, 0) + 1
	total_records = sum(counts.values())
	present = counts.get("Present", 0)
	return {
		"total": len(rows),
		"marked": total_records,
		"present": present,
		"absent": counts.get("Absent", 0),
		"leave": counts.get("Leave", 0),
		"late": counts.get("Late", 0),
		"unmarked": len([row for row in rows if not row.get("status")]),
		"attendance_rate": round((present / total_records) * 100, 2) if total_records else 0,
		"by_status": counts,
	}


@frappe.whitelist()
def get_attendance_status_options():
	"""Return the real Student Attendance status options configured in the DocType."""
	_ensure_attendance_read_permission()
	return _attendance_statuses()


@frappe.whitelist()
def get_attendance_classes():
	"""Return readable Student Groups for attendance filters."""
	if not frappe.has_permission("Student Group", "read"):
		frappe.throw(_("Not permitted to read Student Groups"), frappe.PermissionError)

	return frappe.get_list(
		"Student Group",
		fields=["name", "student_group_name", "program", "academic_year", "group_based_on"],
		filters={"disabled": 0},
		order_by="student_group_name asc",
		limit_page_length=200,
	)


@frappe.whitelist()
def get_attendance_students(student_group):
	"""Return active students in a readable Student Group."""
	students = _get_group_students(student_group)
	student_ids = [student.student for student in students]
	images = {}
	if student_ids and frappe.has_permission("Student", "read"):
		for row in frappe.get_all(
			"Student",
			fields=["name", "image"],
			filters={"name": ["in", student_ids]},
			limit_page_length=len(student_ids),
		):
			images[row.name] = row.image

	return [
		{
			"student": row.student,
			"student_name": row.student_name,
			"group_roll_number": row.group_roll_number,
			"image": images.get(row.student),
		}
		for row in students
	]


@frappe.whitelist()
def get_class_attendance(date, student_group):
	"""Return one-day Student Group attendance using real Student Attendance rows."""
	_ensure_attendance_read_permission()
	attendance_date = _attendance_date(date)
	students = _get_group_students(student_group)
	attendance_rows = frappe.get_list(
		"Student Attendance",
		fields=["name", "student", "student_name", "status", "leave_application", "docstatus"],
		filters={
			"student_group": student_group,
			"date": attendance_date,
			"docstatus": ["!=", 2],
		},
		limit_page_length=max(len(students), 1),
	)
	attendance_by_student = {row.student: row for row in attendance_rows}
	rows = []
	for index, student in enumerate(students, start=1):
		attendance = attendance_by_student.get(student.student) or {}
		rows.append(
			{
				"idx": index,
				"student": student.student,
				"student_name": student.student_name,
				"group_roll_number": student.group_roll_number,
				"attendance": attendance.get("name"),
				"status": attendance.get("status") or "",
				"note": attendance.get("leave_application") or "",
				"docstatus": attendance.get("docstatus"),
			}
		)

	return {
		"date": attendance_date,
		"student_group": student_group,
		"rows": rows,
		"summary": _attendance_summary(rows),
		"status_options": _attendance_statuses(),
		"can_write": 1 if frappe.has_permission("Student Attendance", "write") else 0,
	}


@frappe.whitelist()
def get_student_attendance_history(student, student_group, from_date, to_date):
	"""Return attendance history for a student within a bounded date range."""
	_ensure_attendance_read_permission()
	_ensure_student_read_permission(student)
	_ensure_student_group_read_permission(student_group)
	if not _student_belongs_to_group(student, student_group):
		frappe.throw(_("Student does not belong to the selected Student Group"))

	start_date = _attendance_date(from_date, "from_date")
	end_date = _attendance_date(to_date, "to_date")
	if start_date > end_date:
		frappe.throw(_("From Date must be before To Date"))
	if (end_date - start_date).days > 370:
		frappe.throw(_("Date range cannot exceed 370 days"))

	rows = frappe.get_list(
		"Student Attendance",
		fields=["name", "date", "status", "student", "student_name", "student_group", "leave_application", "docstatus"],
		filters={
			"student": student,
			"student_group": student_group,
			"date": ["between", [start_date, end_date]],
			"docstatus": ["!=", 2],
		},
		order_by="date asc",
		limit_page_length=400,
	)
	student_doc = frappe.get_doc("Student", student)
	response_rows = []
	for index, row in enumerate(rows, start=1):
		response_rows.append(
			{
				"idx": index,
				"name": row.name,
				"date": row.date,
				"status": row.status,
				"note": row.leave_application or "",
			}
		)

	return {
		"student": {
			"name": student_doc.name,
			"student_name": student_doc.student_name,
			"image": student_doc.image,
			"student_group": student_group,
		},
		"rows": response_rows,
		"summary": _attendance_summary(response_rows),
		"status_options": _attendance_statuses(),
	}


@frappe.whitelist()
def get_student_month_attendance(student, student_group, month, year):
	"""Return a student's attendance for one month."""
	from calendar import monthrange
	from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
	from education.education.doctype.student_attendance.student_attendance import get_holiday_list

	month = int(month)
	year = int(year)
	if month < 1 or month > 12:
		frappe.throw(_("Invalid month"))
	start_date = getdate(f"{year}-{month:02d}-01")
	end_date = getdate(f"{year}-{month:02d}-{monthrange(year, month)[1]}")
	response = get_student_attendance_history(student, student_group, start_date, end_date)
	non_working_dates = []
	holiday_warning = ""
	try:
		holiday_list = get_holiday_list()
		cursor = start_date
		while cursor <= end_date:
			if is_holiday(holiday_list, cursor):
				non_working_dates.append(cstr(cursor))
			cursor = add_days(cursor, 1)
	except Exception as exc:
		holiday_warning = cstr(exc)
		non_working_dates = []
	response["non_working_dates"] = non_working_dates
	response["holiday_warning"] = holiday_warning
	return response


@frappe.whitelist()
def save_student_month_attendance(student, student_group, month, year, records):
	"""Create/update/clear Student Attendance rows for one student month."""
	from calendar import monthrange

	if not frappe.has_permission("Student Attendance", "create") and not frappe.has_permission(
		"Student Attendance", "write"
	):
		frappe.throw(_("Not permitted to save student attendance"), frappe.PermissionError)

	_ensure_student_read_permission(student)
	_ensure_student_group_read_permission(student_group)
	if not _student_belongs_to_group(student, student_group):
		frappe.throw(_("Student does not belong to the selected Student Group"))

	month = int(month)
	year = int(year)
	if month < 1 or month > 12:
		frappe.throw(_("Invalid month"))
	start_date = getdate(f"{year}-{month:02d}-01")
	end_date = getdate(f"{year}-{month:02d}-{monthrange(year, month)[1]}")
	records = _school_calendar_json(records, []) or []
	if len(records) > 31:
		frappe.throw(_("Too many attendance records"))

	student_name = frappe.db.get_value("Student", student, "student_name")
	saved = []
	cleared = []
	for row in records:
		attendance_date = _attendance_date(row.get("date"))
		if attendance_date < start_date or attendance_date > end_date:
			frappe.throw(_("Attendance date {0} is outside the selected month").format(attendance_date))
		status = _validate_attendance_status(row.get("status"))
		existing_name = frappe.db.exists(
			"Student Attendance",
			{
				"student": student,
				"student_group": student_group,
				"date": attendance_date,
				"docstatus": ["!=", 2],
			},
		)
		if not status:
			if existing_name:
				doc = frappe.get_doc("Student Attendance", existing_name)
				if not (doc.has_permission("cancel") or doc.has_permission("delete")):
					frappe.throw(_("Not permitted to clear attendance for {0}").format(attendance_date))
				if doc.docstatus == 1:
					doc.cancel()
				if doc.has_permission("delete"):
					frappe.delete_doc("Student Attendance", doc.name)
				cleared.append(cstr(attendance_date))
			continue

		if existing_name:
			doc = frappe.get_doc("Student Attendance", existing_name)
			if not doc.has_permission("write"):
				frappe.throw(_("Not permitted to update attendance for {0}").format(attendance_date))
			doc.status = status
			doc.save()
		else:
			if not frappe.has_permission("Student Attendance", "create"):
				frappe.throw(_("Not permitted to create attendance for {0}").format(attendance_date))
			doc = frappe.new_doc("Student Attendance")
			doc.student = student
			doc.student_name = student_name
			doc.student_group = student_group
			doc.date = attendance_date
			doc.status = status
			doc.insert()
			doc.submit()
		saved.append({"date": attendance_date, "status": status, "name": doc.name})

	return {
		"saved": saved,
		"cleared": cleared,
		"month": month,
		"year": year,
	}
