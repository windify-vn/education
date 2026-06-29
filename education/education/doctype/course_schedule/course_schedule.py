# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt


from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, cint, getdate, to_timedelta


WEEKDAY_FIELDS = [
	"monday",
	"tuesday",
	"wednesday",
	"thursday",
	"friday",
	"saturday",
	"sunday",
]


class CourseSchedule(Document):
	def validate(self):
		self.set_student_group_defaults()
		self.validate_topic_immutable()
		self.validate_topic()

		if self.is_new() and cint(getattr(self, "create_recurring_schedule", 0)):
			if not self.start_date or not self.end_date:
				frappe.throw(_("Please set Start Date and End Date for the Course/Student Group to create a recurring schedule."))

			import calendar

			date = getdate(self.start_date)
			end_date = getdate(self.end_date)
			valid_date = None

			selected_days = [d.title() for d in WEEKDAY_FIELDS if self.get(d)]
			if not selected_days:
				frappe.throw(_("Please select at least one weekday."))

			while date <= end_date:
				if calendar.day_name[date.weekday()] in selected_days:
					valid_date = date
					break
				date = add_days(date, 1)

			if not valid_date:
				frappe.throw(_("No matching weekday found between Start Date and End Date."))

			self.schedule_date = valid_date
			self.flags.recurring_dates = []

			curr = valid_date
			while curr <= end_date:
				if calendar.day_name[curr.weekday()] in selected_days:
					self.flags.recurring_dates.append(curr)
				curr = add_days(curr, 1)

		self.normalize_calendar_datetime()
		self.set_default_weekday()
		self.validate_duration()
		self.set_end_time()
		self.instructor_name = frappe.db.get_value(
			"Instructor", self.instructor, "instructor_name"
		)
		self.set_title()
		self.validate_course()
		self.validate_date()
		self.validate_time()
		self.validate_weekdays()
		self.validate_overlap()

	def before_save(self):
		self.set_hex_color()

	def validate_topic_immutable(self):
		if not self.is_new() and self.has_value_changed("topic"):
			frappe.throw(
				_("Topic cannot be changed after a Course Schedule has been created."),
				title=_("Topic Is Locked"),
			)

	def validate_topic(self):
		if not self.topic or not self.course:
			return

		if not frappe.db.exists("Course Topic", {"parent": self.course, "topic": self.topic}):
			frappe.throw(
				_("Topic {0} does not belong to Course {1}.").format(
					frappe.bold(self.topic), frappe.bold(self.course)
				),
				title=_("Invalid Topic"),
			)

		if not self.is_new() and not self.has_value_changed("topic"):
			return

		duplicate_schedule = frappe.db.exists(
			"Course Schedule",
			{
				"name": ("!=", self.name),
				"course": self.course,
				"topic": self.topic,
				"docstatus": ("!=", 2),
			},
		)
		if duplicate_schedule:
			frappe.throw(
				_("Topic {0} is already assigned to Course Schedule {1}.").format(
					frappe.bold(self.topic), frappe.bold(duplicate_schedule)
				),
				title=_("Topic Already Scheduled"),
			)

	def on_trash(self):
		self.validate_no_attendance_records()
		self.reflow_recurring_topics_after_delete()

	def validate_no_attendance_records(self):
		attendance_record = frappe.db.exists(
			"Student Attendance",
			{"course_schedule": self.name, "docstatus": ("!=", 2)},
		)
		if attendance_record:
			frappe.throw(
				_(
					"Cannot delete Course Schedule {0} because attendance has already been marked."
				).format(frappe.bold(self.name)),
				title=_("Attendance Exists"),
			)

	def reflow_recurring_topics_after_delete(self):
		if not self.should_reflow_recurring_topics():
			return

		topics = self.get_course_topics()
		if not topics:
			return

		series_schedules = self.get_recurring_series_schedules()
		if not series_schedules:
			return

		recurring_dates = self.get_recurring_dates(
			exclude_date=getdate(self.schedule_date)
		)[: len(topics)]
		if not recurring_dates:
			return

		schedules_by_date = {}
		for schedule in series_schedules:
			schedule_date = getdate(schedule.schedule_date)
			if schedule_date not in schedules_by_date:
				schedules_by_date[schedule_date] = schedule

		planned_updates = []
		planned_inserts = []
		for index, schedule_date in enumerate(recurring_dates):
			topic = topics[index]
			schedule = schedules_by_date.get(schedule_date)
			if schedule:
				if schedule.topic != topic:
					planned_updates.append((schedule, topic))
			else:
				planned_inserts.append((schedule_date, topic))

		self.validate_reflow_attendance(planned_updates)

		for schedule, topic in planned_updates:
			frappe.db.set_value("Course Schedule", schedule.name, "topic", topic)

		for schedule_date, topic in planned_inserts:
			new_schedule = frappe.copy_doc(self)
			new_schedule.schedule_date = schedule_date
			new_schedule.topic = topic
			new_schedule.create_recurring_schedule = 0
			new_schedule.insert(ignore_permissions=True)

	def should_reflow_recurring_topics(self):
		return bool(
			self.course
			and self.topic
			and self.student_group
			and self.start_date
			and self.end_date
			and self.schedule_date
			and any(cint(self.get(fieldname)) for fieldname in WEEKDAY_FIELDS)
		)

	def get_course_topics(self):
		return frappe.get_all(
			"Course Topic",
			filters={"parent": self.course},
			order_by="idx asc",
			pluck="topic",
		)

	def get_recurring_dates(self, exclude_date=None):
		selected_weekdays = {
			index for index, fieldname in enumerate(WEEKDAY_FIELDS) if cint(self.get(fieldname))
		}
		if not selected_weekdays:
			return []

		exclude_date = getdate(exclude_date) if exclude_date else None
		date = getdate(self.start_date)
		end_date = getdate(self.end_date)
		recurring_dates = []

		while date <= end_date:
			if date.weekday() in selected_weekdays and date != exclude_date:
				recurring_dates.append(date)
			date = add_days(date, 1)

		return recurring_dates

	def get_recurring_series_schedules(self):
		filters = {
			"name": ("!=", self.name),
			"docstatus": ("!=", 2),
			"student_group": self.student_group,
			"course": self.course,
			"start_date": self.start_date,
			"end_date": self.end_date,
			"from_time": self.from_time,
			"duration": self.duration,
		}
		for fieldname in WEEKDAY_FIELDS:
			filters[fieldname] = cint(self.get(fieldname))

		return frappe.get_all(
			"Course Schedule",
			filters=filters,
			fields=["name", "schedule_date", "topic"],
			order_by="schedule_date asc, creation asc",
		)

	def validate_reflow_attendance(self, planned_updates):
		schedule_names = [schedule.name for schedule, topic in planned_updates]
		if not schedule_names:
			return

		attendance_record = frappe.db.exists(
			"Student Attendance",
			{
				"course_schedule": ("in", schedule_names),
				"docstatus": ("!=", 2),
			},
		)
		if attendance_record:
			frappe.throw(
				_(
					"Cannot delete this Course Schedule because later schedules already have attendance and topics cannot be shifted."
				),
				title=_("Attendance Exists"),
			)

	def set_title(self):
		"""Set document Title"""
		title_parts = [str(self.schedule_date or ""), self.course]
		self.title = " - ".join([part for part in title_parts if part])

	def set_student_group_defaults(self):
		if not self.student_group:
			return

		student_group = frappe.db.get_value(
			"Student Group",
			self.student_group,
			["program", "course", "group_based_on", "start_date", "end_date"],
			as_dict=True,
		)
		if not student_group:
			return

		self.program = student_group.program
		if student_group.group_based_on == "Course" and student_group.course:
			self.course = student_group.course

		self.start_date = student_group.start_date
		self.end_date = student_group.end_date

		instructors = frappe.get_all(
			"Student Group Instructor",
			filters={"parent": self.student_group},
			pluck="instructor",
		)
		if len(instructors) == 1 and not self.instructor:
			self.instructor = instructors[0]

	def validate_course(self):
		group_based_on, course = frappe.db.get_value(
			"Student Group", self.student_group, ["group_based_on", "course"]
		)
		if group_based_on == "Course":
			self.course = course

	def validate_date(self):
		start_date, end_date = frappe.db.get_value(
			"Student Group", self.student_group, ["start_date", "end_date"]
		)
		self.schedule_date = getdate(self.schedule_date)

		if start_date and end_date and (self.schedule_date < getdate(start_date) or self.schedule_date > getdate(end_date)):
			frappe.throw(
				_(
					"Schedule date selected does not lie within the Start Date and End Date of the Student Group {0}."
				).format(self.student_group)
			)

	def validate_time(self):
		"""Validates if from_time is greater than to_time"""
		if to_timedelta(self.from_time) > to_timedelta(self.to_time):
			frappe.throw(_("Start Time cannot be greater than End Time."))

	def normalize_calendar_datetime(self):
		"""Handles specific case to update schedule date from calendar drag/drop."""
		if isinstance(self.from_time, str):
			try:
				datetime_obj = datetime.strptime(self.from_time, "%Y-%m-%d %H:%M:%S")
				self.schedule_date = datetime_obj.date()
				self.from_time = datetime_obj.time()
			except ValueError:
				pass

	def validate_duration(self):
		self.duration = cint(self.duration or 0)
		if self.duration <= 0:
			frappe.throw(_("Duration must be greater than 0 minutes."))

	def set_end_time(self):
		if self.from_time and self.duration:
			self.to_time = to_timedelta(self.from_time) + timedelta(minutes=self.duration)

	def set_default_weekday(self):
		if any(cint(self.get(fieldname)) for fieldname in WEEKDAY_FIELDS) or not self.schedule_date:
			return

		weekday = getdate(self.schedule_date).weekday()
		self.set(WEEKDAY_FIELDS[weekday], 1)

	def validate_weekdays(self):
		if not any(cint(self.get(fieldname)) for fieldname in WEEKDAY_FIELDS):
			frappe.throw(_("Please select at least one weekday."))

	def validate_overlap(self):
		"""Validates overlap for Student Group, Instructor, Room"""

		from education.education.utils import validate_overlap_for

		# Validate overlapping course schedules.
		if self.student_group:
			validate_overlap_for(self, "Course Schedule", "student_group")

		validate_overlap_for(self, "Course Schedule", "instructor")
		validate_overlap_for(self, "Course Schedule", "room")

		# validate overlapping assessment schedules.
		if self.student_group:
			validate_overlap_for(self, "Assessment Plan", "student_group")

		validate_overlap_for(self, "Assessment Plan", "room")
		validate_overlap_for(self, "Assessment Plan", "supervisor", self.instructor)

	def set_hex_color(self):
		colors = {
			"blue": "#EDF6FD",
			"green": "#E4F5E9",
			"red": "#FFF0F0",
			"orange": "#FFF1E7",
			"yellow": "#FFF7D3",
			"teal": "#E6F7F4",
			"violet": "#F5F2FF",
			"cyan": "#E0F8FF",
			"amber": "#FCF3CF",
			"pink": "#FEEEF8",
			"purple": "#F9F0FF",
		}
		self.color = colors[self.class_schedule_color or "green"]

	def after_insert(self):
		if cint(getattr(self, "create_recurring_schedule", 0)) and getattr(self.flags, "recurring_dates", None):
			topics = frappe.get_all("Course Topic", filters={"parent": self.course}, order_by="idx asc", pluck="topic")
			recurring_dates = self.flags.recurring_dates[: len(topics)] if topics else self.flags.recurring_dates

			first_topic = topics[0] if topics else None
			if first_topic:
				frappe.db.set_value("Course Schedule", self.name, "topic", first_topic)
			self.create_recurring_schedule = 0

			for i in range(1, len(recurring_dates)):
				date = recurring_dates[i]
				topic = topics[i] if i < len(topics) else None

				new_schedule = frappe.copy_doc(self)
				new_schedule.schedule_date = date
				new_schedule.topic = topic
				new_schedule.create_recurring_schedule = 0
				new_schedule.insert(ignore_permissions=True)
