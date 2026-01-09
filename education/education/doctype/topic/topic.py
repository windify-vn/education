# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json

import frappe
from frappe import _
from frappe.model.document import Document


class Topic(Document):
	def get_contents(self):
		try:
			topic_content_list = self.topic_content
			content_data = [
				frappe.get_doc(topic_content.content_type, topic_content.content)
				for topic_content in topic_content_list
			]
		except Exception as e:
			frappe.log_error(frappe.get_traceback())
			return None
		return content_data

	def on_update(self):
		"""Update linked_topic field in Homework when Topic is saved"""
		self.update_homework_linked_topic()

	def update_homework_linked_topic(self):
		"""
		Set linked_topic field for all homeworks in custom_homework child table.
		Business rule: 1 Homework can only belong to 1 Topic.
		When homework is added to this Topic, remove it from other Topics.
		"""
		if not hasattr(self, 'custom_homework') or not self.custom_homework:
			return
		
		# Get list of homework names in this Topic
		current_homework_names = [hw.homework for hw in self.custom_homework if hw.homework]
		
		for hw_name in current_homework_names:
			# Update the linked_topic field in Homework
			frappe.db.set_value('Homework', hw_name, 'linked_topic', self.name, update_modified=False)
			
			# Remove this homework from ALL other Topics (ensure 1:1 relationship)
			frappe.db.delete('Topic Homework', {
				'homework': hw_name,
				'parenttype': 'Topic',
				'parent': ['!=', self.name]
			})


@frappe.whitelist()
def get_courses_without_topic(topic):
	data = []
	for entry in frappe.db.get_all("Course"):
		course = frappe.get_doc("Course", entry.name)
		topics = [t.topic for t in course.topics]
		if not topics or topic not in topics:
			data.append(course.name)
	return data


@frappe.whitelist()
def add_topic_to_courses(topic, courses, mandatory=False):
	courses = json.loads(courses)
	for entry in courses:
		course = frappe.get_doc("Course", entry)
		course.append("topics", {"topic": topic, "topic_name": topic})
		course.flags.ignore_mandatory = True
		course.save()
	frappe.db.commit()
	frappe.msgprint(
		_("Topic {0} has been added to all the selected courses successfully.").format(
			frappe.bold(topic)
		),
		title=_("Courses updated"),
		indicator="green",
	)


@frappe.whitelist()
def add_content_to_topics(content_type, content, topics):
	topics = json.loads(topics)
	for entry in topics:
		topic = frappe.get_doc("Topic", entry)
		topic.append(
			"topic_content",
			{
				"content_type": content_type,
				"content": content,
			},
		)
		topic.flags.ignore_mandatory = True
		topic.save()
	frappe.db.commit()
	frappe.msgprint(
		_("{0} {1} has been added to all the selected topics successfully.").format(
			content_type, frappe.bold(content)
		),
		title=_("Topics updated"),
		indicator="green",
	)
