const COURSE_SCHEDULE_WEEKDAYS = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
]

frappe.ui.form.on('Course Schedule', {
  setup(frm) {
    frm.instructors = []
    frm.course_schedule_has_attendance = null
    frm._course_schedule_original_topic = null
    frm._create_recurring_schedule = 0

    if (!frm._course_schedule_original_savetrash) {
      frm._course_schedule_original_savetrash = frm.savetrash.bind(frm)
      frm.savetrash = () => {
        if (frm.course_schedule_has_attendance) {
          show_attendance_delete_guard_message()
          return
        }

        if (frm.course_schedule_has_attendance === null && !frm.doc.__islocal) {
          frappe.call({
            method: 'education.education.api.course_schedule_has_attendance',
            args: {
              course_schedule: frm.doc.name,
            },
            freeze: true,
            callback(r) {
              frm.course_schedule_has_attendance = Boolean(r.message)
              if (frm.course_schedule_has_attendance) {
                frm.events.apply_attendance_delete_guard(frm)
                show_attendance_delete_guard_message()
                return
              }
              frm._course_schedule_original_savetrash()
            },
          })
          return
        }

        frm._course_schedule_original_savetrash()
      }
    }

    frm.set_query('instructor', () => {
      if (frm.doc.student_group) {
        return {
          filters: {
            name: ['in', frm.instructors.length ? frm.instructors : ['']],
          },
        }
      }
    })

    frm.set_query('course', () => {
      return {
        query:
          'education.education.doctype.program_enrollment.program_enrollment.get_program_courses',
        filters: {
          program: frm.doc.program,
        },
      }
    })

    frm.set_query('topic', () => {
      return {
        query: 'education.education.api.get_available_course_schedule_topics',
        filters: {
          course: frm.doc.course,
          course_schedule: frm.doc.name,
        },
      }
    })
  },

  refresh(frm) {
    frm.toggle_display('naming_series', false)
    frm.events.setup_recurring_schedule_toggle(frm)

    if (!frm.doc.__islocal) {
      frm.add_custom_button(__('Mark Attendance'), () => {
        frappe.route_options = {
          based_on: 'Course Schedule',
          course_schedule: frm.doc.name,
        }
        frappe.set_route('Form', 'Student Attendance Tool')
      })
    }

    if (frm.doc.student_group) {
      frm.events.set_student_group_defaults(frm, {
        preserve_existing_instructor: !frm.doc.__islocal,
      })
    }
    frm.events.toggle_instructor_editable(frm)
    frm.events.toggle_recurring_schedule_fields(frm)
    frm.events.toggle_topic_editable(frm)
    frm.events.cache_original_topic(frm)
    if (!frm.doc.__islocal) {
      setTimeout(() => frm.events.show_saved_topic_fields(frm), 0)
    }
    frm.events.calculate_end_time(frm)
    frm.events.set_schedule_weekday(frm)
    frm.events.set_attendance_delete_guard(frm)
    frm.events.apply_permission_ui(frm)
  },

  student_group(frm) {
    frm.events.toggle_instructor_editable(frm)
    frm.events.set_student_group_defaults(frm)
  },

  schedule_date(frm) {
    frm.events.set_schedule_weekday(frm)
  },

  from_time(frm) {
    frm.events.calculate_end_time(frm)
  },

  duration(frm) {
    frm.events.calculate_end_time(frm)
  },

  topic(frm) {
    frm.events.validate_topic_change(frm, true)
  },

  validate(frm) {
    frm.events.sync_recurring_schedule_flag(frm)
    frm.events.validate_topic_change(frm)
  },

  set_attendance_delete_guard(frm) {
    frm.course_schedule_has_attendance = null

    if (frm.doc.__islocal) return

    frappe.call({
      method: 'education.education.api.course_schedule_has_attendance',
      args: {
        course_schedule: frm.doc.name,
      },
      callback(r) {
        frm.course_schedule_has_attendance = Boolean(r.message)
        if (frm.course_schedule_has_attendance) {
          frm.events.apply_attendance_delete_guard(frm)
        }
      },
    })
  },

  apply_attendance_delete_guard(frm) {
    frm.dashboard.set_headline_alert(
      __('Attendance has already been marked. This schedule cannot be deleted.'),
      'orange'
    )
    remove_delete_menu_item(frm)
    setTimeout(() => remove_delete_menu_item(frm), 0)
  },

  cache_original_topic(frm) {
    if (frm.doc.__islocal) return
    frm._course_schedule_original_topic = frm.doc.topic || ''
  },

  toggle_topic_editable(frm) {
    frm.set_df_property('topic', 'read_only', !frm.doc.__islocal)
  },

  show_saved_topic_fields(frm) {
    const topic_fields = ['topic', 'topic_name']
    topic_fields.forEach((fieldname) => {
      frm.set_df_property(fieldname, 'depends_on', '')
      frm.set_df_property(fieldname, 'hidden', 0)
      frm.toggle_display(fieldname, true)
      frm.refresh_field(fieldname)
    })
    frm.set_df_property('topic', 'read_only', 1)
  },

  toggle_instructor_editable(frm) {
    const can_select_instructor = !frm.doc.__islocal || Boolean(frm.doc.student_group)
    frm.set_df_property('instructor', 'hidden', 0)
    frm.toggle_display('instructor', true)
    frm.toggle_enable('instructor', can_select_instructor)
    frm.refresh_field('instructor')
  },

  setup_recurring_schedule_toggle(frm) {
    if (!frm.doc.__islocal) {
      frm._create_recurring_schedule = 0
      frm.doc.create_recurring_schedule = 0
      if (frm.$recurring_schedule_toggle) {
        frm.$recurring_schedule_toggle.hide()
      }
      return
    }

    const $anchor = frm.fields_dict.class_schedule_color
      && frm.fields_dict.class_schedule_color.$wrapper
    if (!$anchor || !$anchor.length) return

    if (
      !frm.$recurring_schedule_toggle
      || !frm.$recurring_schedule_toggle.length
      || !document.body.contains(frm.$recurring_schedule_toggle[0])
    ) {
      frm.$recurring_schedule_toggle = $(`
        <div class="frappe-control input-max-width course-recurring-schedule-toggle">
          <div class="checkbox">
            <label>
              <span class="input-area">
                <input type="checkbox" data-fieldname="create_recurring_schedule" />
              </span>
              <span class="label-area">${__('Create Recurring Schedule')}</span>
            </label>
          </div>
        </div>
      `)
      $anchor.after(frm.$recurring_schedule_toggle)
      frm.$recurring_schedule_toggle.on('change', 'input[type="checkbox"]', () => {
        frm._create_recurring_schedule = frm.$recurring_schedule_toggle
          .find('input[type="checkbox"]')
          .is(':checked')
          ? 1
          : 0
        frm.events.sync_recurring_schedule_flag(frm)
        frm.events.toggle_recurring_schedule_fields(frm)
      })
    }

    frm.$recurring_schedule_toggle.show()
    frm.$recurring_schedule_toggle
      .find('input[type="checkbox"]')
      .prop('checked', Boolean(to_int(frm._create_recurring_schedule)))
    frm.events.sync_recurring_schedule_flag(frm)
  },

  sync_recurring_schedule_flag(frm) {
    frm.doc.create_recurring_schedule = frm.doc.__islocal
      ? to_int(frm._create_recurring_schedule)
      : 0
  },

  apply_permission_ui(frm) {
    const can_create = can_model('create', frm.doctype)
    const can_write = can_model('write', frm.doctype)
    const can_delete = can_model('delete', frm.doctype)

    if (frm.$recurring_schedule_toggle) {
      frm.$recurring_schedule_toggle
        .find('input[type="checkbox"]')
        .prop('disabled', !can_create || !frm.doc.__islocal)
    }

    if (frm.doc.__islocal && !can_create) {
      frm.disable_form()
      frm.dashboard.set_headline_alert(
        __('You have read-only access to Course Schedule.'),
        'blue'
      )
      return
    }

    if (!frm.doc.__islocal && !can_write) {
      frm.disable_form()
      frm.dashboard.set_headline_alert(
        __('You have read-only access to this Course Schedule.'),
        'blue'
      )
      frm.events.show_saved_topic_fields(frm)
      setTimeout(() => frm.events.show_saved_topic_fields(frm), 0)
    }

    if (!can_delete) {
      remove_delete_menu_item(frm)
      setTimeout(() => remove_delete_menu_item(frm), 0)
    }
  },

  validate_topic_change(frm, restore = false) {
    if (
      frm.doc.__islocal ||
      frm._course_schedule_original_topic === null ||
      (frm.doc.topic || '') === frm._course_schedule_original_topic
    ) {
      return
    }

    if (restore) {
      frappe.show_alert({
        message: __('Topic cannot be changed after a Course Schedule has been created.'),
        indicator: 'orange',
      })
      frm.set_value('topic', frm._course_schedule_original_topic)
      return
    }

    frappe.throw(__('Topic cannot be changed after a Course Schedule has been created.'))
  },

  set_student_group_defaults(frm, options = {}) {
    frm.instructors = []
    if (!frm.doc.student_group) {
      frm.set_value({
        program: '',
        course: '',
        start_date: '',
        end_date: '',
        instructor: '',
      })
      frm.events.toggle_instructor_editable(frm)
      return
    }

    frappe.call({
      method: 'education.education.api.get_course_schedule_student_group_defaults',
      args: {
        student_group: frm.doc.student_group,
      },
      callback(data) {
        const defaults = data.message || {}
        frm.instructors = defaults.instructors || []
        let instructor = frm.doc.instructor
        if (options.preserve_existing_instructor && instructor) {
          // Keep saved schedules stable while still refreshing instructor options.
        } else if (frm.instructors.length === 1) {
          instructor = frm.instructors[0]
        } else if (!instructor || !frm.instructors.includes(instructor)) {
          instructor = ''
        }
        frm.set_value({
          program: defaults.program || '',
          course: defaults.course || '',
          start_date: defaults.start_date || '',
          end_date: defaults.end_date || '',
          instructor,
        })
      },
    })
  },

  toggle_recurring_schedule_fields(frm) {
    const is_recurring = frm.doc.__islocal && to_int(frm._create_recurring_schedule)
    frm.toggle_display('schedule_date', !is_recurring)
    frm.toggle_display('start_date', is_recurring)
    frm.toggle_display('end_date', is_recurring)
    frm.toggle_display('weekday_configuration_section', is_recurring)
    COURSE_SCHEDULE_WEEKDAYS.forEach((fieldname) => {
      frm.toggle_display(fieldname, is_recurring)
    })

    if (!frm.doc.__islocal) {
      frm.toggle_display('schedule_date', true)
      frm.toggle_display('start_date', false)
      frm.toggle_display('end_date', false)
      frm.toggle_display('weekday_configuration_section', false)
      COURSE_SCHEDULE_WEEKDAYS.forEach((fieldname) => {
        frm.toggle_display(fieldname, false)
      })
      frm.events.show_saved_topic_fields(frm)
      return
    }

    const show_topic = !is_recurring
    frm.toggle_display('topic', show_topic)
    frm.toggle_display('topic_name', show_topic)
  },

  calculate_end_time(frm) {
    const start_minutes = get_time_minutes(frm.doc.from_time)
    const duration = to_int(frm.doc.duration || 0)
    if (start_minutes === null || duration <= 0) return

    frm.set_value('to_time', get_time_string(start_minutes + duration))
  },

  set_schedule_weekday(frm) {
    if (!frm.doc.schedule_date) return
    const has_weekday = COURSE_SCHEDULE_WEEKDAYS.some((fieldname) =>
      to_int(frm.doc[fieldname])
    )
    if (has_weekday) return

    const weekday = frappe.datetime.str_to_obj(frm.doc.schedule_date).getDay()
    const monday_based_index = weekday === 0 ? 6 : weekday - 1
    frm.set_value(COURSE_SCHEDULE_WEEKDAYS[monday_based_index], 1)
  },
})

function get_time_minutes(value) {
  if (!value) return null
  const parts = String(value).split(':').map((part) => to_int(part))
  if (parts.length < 2) return null
  return parts[0] * 60 + parts[1]
}

function to_int(value) {
  return Number.parseInt(value || 0, 10) || 0
}

function get_time_string(total_minutes) {
  const minutes_in_day = 24 * 60
  const normalized_minutes =
    ((total_minutes % minutes_in_day) + minutes_in_day) % minutes_in_day
  const hours = Math.floor(normalized_minutes / 60)
  const minutes = normalized_minutes % 60
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:00`
}

function show_attendance_delete_guard_message() {
  frappe.msgprint({
    title: __('Attendance Exists'),
    indicator: 'orange',
    message: __(
      'Cannot delete this Course Schedule because attendance has already been marked.'
    ),
  })
}

function remove_delete_menu_item(frm) {
  frm.page.menu
    .find('.menu-item-label')
    .filter((_, item) => $(item).text().trim() === __('Delete'))
    .closest('li')
    .remove()
}

function can_model(permission, doctype) {
  const checker = frappe.model && frappe.model[`can_${permission}`]
  return checker ? Boolean(checker(doctype)) : true
}
