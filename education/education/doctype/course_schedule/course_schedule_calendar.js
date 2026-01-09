frappe.views.calendar['Course Schedule'] = {
  field_map: {
    start: 'from_time',
    end: 'to_time',
    id: 'name',
    title: 'title',
    allDay: 'allDay',
  },
  gantt: true,
  order_by: 'schedule_date',
  filters: [
    {
      fieldtype: 'Link',
      fieldname: 'student_group',
      options: 'Student Group',
      label: __('Student Group'),
    },
    {
      fieldtype: 'Link',
      fieldname: 'course',
      options: 'Course',
      label: __('Course'),
    },
    {
      fieldtype: 'Link',
      fieldname: 'instructor',
      options: 'Instructor',
      label: __('Instructor'),
    },
    {
      fieldtype: 'Link',
      fieldname: 'room',
      options: 'Room',
      label: __('Room'),
    },
  ],
  get_events_method: 'education.education.api.get_course_schedule_events',
  eventRender: function(event, element) {
    // Find the title element, supporting different versions of FullCalendar
    const title_element = element.find('.fc-event-title, .fc-title');
    
    // Apply CSS to preserve whitespace and wrap text
    // This will respect the '\n' characters from the backend
    title_element.css('white-space', 'pre-wrap');
  }
}
