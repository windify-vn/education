// Custom script for Homework DocType
frappe.ui.form.on('Homework', {
  setup: function (frm) {
    // Set query for student_group field to show all Student Groups (no limit)
    frm.set_query('student_group', function () {
      return {
        page_length: 0,
      }
    })
  },

  refresh: function (frm) {
    // Make course field read-only (auto-populated from student_group)
    frm.set_df_property('course', 'read_only', 1)

    // Set query for linked_topic based on course
    frm.trigger('set_topic_query')

    // If student_group is set but course is empty, fetch and set course
    if (frm.doc.student_group && !frm.doc.course) {
      frappe.db.get_value(
        'Student Group',
        frm.doc.student_group,
        'course',
        function (r) {
          if (r && r.course) {
            frm.set_value('course', r.course)
          }
        }
      )
    }
  },

  set_topic_query: function (frm) {
    // Filter linked_topic by topics that belong to the selected course
    if (frm.doc.course) {
      // Get topics from Course using custom API
      frappe.call({
        method: 'education.education.api.get_course_topics',
        args: {
          course: frm.doc.course,
        },
        async: false,
        callback: function (r) {
          if (r.message && r.message.length > 0) {
            frm.set_query('linked_topic', function () {
              return {
                filters: {
                  name: ['in', r.message],
                },
                page_length: 0, // Show all topics
              }
            })
          } else {
            // No topics in this course
            frm.set_query('linked_topic', function () {
              return {
                filters: {
                  name: ['in', ['__no_topic__']],
                },
              }
            })
          }
        },
      })
    } else {
      // No course selected, show all topics
      frm.set_query('linked_topic', function () {
        return {
          page_length: 0,
        }
      })
    }
  },

  student_group: function (frm) {
    // When student_group changes, fetch the course from Student Group
    if (frm.doc.student_group) {
      frappe.db.get_value(
        'Student Group',
        frm.doc.student_group,
        'course',
        function (r) {
          if (r && r.course) {
            frm.set_value('course', r.course)
          } else {
            frm.set_value('course', null)
          }
          // Clear linked_topic when student_group changes
          frm.set_value('linked_topic', null)
        }
      )
    } else {
      frm.set_value('course', null)
      frm.set_value('linked_topic', null)
    }
  },

  course: function (frm) {
    // When course changes, update topic query and clear linked_topic
    frm.trigger('set_topic_query')
    if (frm.__course_changed) {
      frm.set_value('linked_topic', null)
    }
    frm.__course_changed = true
  },
})
