// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student', {
  refresh: function (frm) {
    frm.set_query('user', function (doc) {
      return {
        filters: {
          ignore_user_type: 1,
        },
      }
    })

    if (!frm.is_new()) {
      frm.add_custom_button(__('Accounting Ledger'), function () {
        frappe.set_route('query-report', 'General Ledger', {
          party_type: 'Customer',
          party: frm.doc.customer,
        })
      })

      // Hide all badges immediately on load (before API call)
      hide_all_badges(frm)

      // Load student groups for Group name select field
      load_student_groups(frm)
    }

    frappe.db
      .get_single_value('Education Settings', 'user_creation_skip')
      .then((r) => {
        if (cint(r) !== 1) {
          frm.set_df_property('student_email_id', 'reqd', 1)
        }
      })
  },

  // When Group name changes, filter List Badge table
  custom_group_name: function (frm) {
    filter_badges_by_group(frm)
  },

  // Before save: set total badge point to ALL badges total (not just selected group)
  before_save: function (frm) {
    let badges = frm.doc.custom_list_badge || []
    let all_total = 0
    badges.forEach((badge) => {
      all_total += flt(badge.badge_points) || 0
    })
    frm.doc.custom_total_badge_point = all_total
  },

  // After save: restore display to show group total
  after_save: function (frm) {
    setTimeout(() => {
      calculate_total_badge_points(frm)
    }, 100)
  },
})

// Hide all badges immediately (to prevent flash)
function hide_all_badges(frm) {
  let badges = frm.doc.custom_list_badge || []
  badges.forEach((badge, arr_idx) => {
    let row = frm.fields_dict.custom_list_badge.grid.grid_rows[arr_idx]
    if (row) {
      $(row.wrapper).hide()
    }
  })

  // Hide total field to prevent flash (will show after calculation)
  frm.get_field('custom_total_badge_point').$wrapper.css('visibility', 'hidden')
}

// Load student groups that this student belongs to
function load_student_groups(frm) {
  if (!frm.doc.name) return

  // Set query to filter custom_group_name Link field
  // Only show groups that this student belongs to
  frm.set_query('custom_group_name', function () {
    return {
      query: 'education.education.api.get_student_groups_for_link',
      filters: {
        student: frm.doc.name,
      },
    }
  })

  // Load groups and auto-select first one if not set
  frappe.call({
    method: 'education.education.api.get_student_groups_for_student',
    args: {
      student: frm.doc.name,
    },
    callback: function (r) {
      if (r.message && r.message.length > 0) {
        let groups = r.message

        // Auto-select first group if not already selected
        if (!frm.doc.custom_group_name) {
          frm.set_value('custom_group_name', groups[0])
        }

        // Always filter badges after a delay to ensure we run LAST
        // This handles race condition with other scripts
        setTimeout(() => {
          filter_badges_by_group(frm)
        }, 200)
      } else {
        // No groups found, show field with 0
        frm.doc.custom_total_badge_point = 0
        frm.refresh_field('custom_total_badge_point')
        frm
          .get_field('custom_total_badge_point')
          .$wrapper.css('visibility', 'visible')
      }
    },
  })
}

// Filter badges table to show only badges for selected group
function filter_badges_by_group(frm) {
  let group_name = frm.doc.custom_group_name
  let badges = frm.doc.custom_list_badge || []

  // If no group selected, hide all badges
  if (!group_name) {
    badges.forEach((badge, arr_idx) => {
      let row = frm.fields_dict.custom_list_badge.grid.grid_rows[arr_idx]
      if (row) {
        $(row.wrapper).hide()
      }
    })
    frm.doc.custom_total_badge_point = 0
    frm.refresh_field('custom_total_badge_point')
    frm
      .get_field('custom_total_badge_point')
      .$wrapper.css('visibility', 'visible')
    return
  }

  // Re-index badges for selected group (display idx 1, 2, 3... for visible badges)
  let visible_idx = 1
  badges.forEach((badge, arr_idx) => {
    let row = frm.fields_dict.custom_list_badge.grid.grid_rows[arr_idx]
    if (row) {
      if (badge.student_group === group_name) {
        // Update idx for visible badges in this group
        badge.idx = visible_idx++
        $(row.wrapper).show()
      } else {
        $(row.wrapper).hide()
      }
    }
  })

  frm.refresh_field('custom_list_badge')

  // Recalculate total for selected group
  calculate_total_badge_points(frm)
}

// Auto-set student_group when adding new badge
frappe.ui.form.on('Student Badge', {
  custom_list_badge_add: function (frm, cdt, cdn) {
    let group_name = frm.doc.custom_group_name

    if (group_name) {
      // Set student_group for new badge
      frappe.model.set_value(cdt, cdn, 'student_group', group_name)

      // Fix idx immediately (synchronous)
      let badges = frm.doc.custom_list_badge || []
      let group_badge_count = badges.filter(
        (b) => b.student_group === group_name && b.name !== cdn
      ).length

      let row = frappe.get_doc(cdt, cdn)
      if (row) {
        row.idx = group_badge_count + 1
      }
    }

    // Recalculate total and refresh
    calculate_total_badge_points(frm)
    frm.refresh_field('custom_list_badge')
    filter_badges_by_group(frm)
  },

  custom_list_badge_remove: function (frm) {
    // Recalculate total after removing
    calculate_total_badge_points(frm)

    // Re-index badges for selected group
    reindex_badges_for_group(frm)
  },

  badge_points: function (frm) {
    // Recalculate total when points change
    calculate_total_badge_points(frm)
  },
})

// Re-index badges for selected group after removal
function reindex_badges_for_group(frm) {
  let group_name = frm.doc.custom_group_name
  if (!group_name) return

  let badges = frm.doc.custom_list_badge || []
  let idx = 1

  badges.forEach((badge) => {
    if (badge.student_group === group_name) {
      badge.idx = idx++
    }
  })

  frm.refresh_field('custom_list_badge')
  filter_badges_by_group(frm)
}

// Calculate total badge points for selected group only (display only, not saved)
function calculate_total_badge_points(frm) {
  let badges = frm.doc.custom_list_badge || []
  let group_name = frm.doc.custom_group_name

  // If no group selected, show 0
  if (!group_name) {
    frm.doc.custom_total_badge_point = 0
    frm.refresh_field('custom_total_badge_point')
    frm
      .get_field('custom_total_badge_point')
      .$wrapper.css('visibility', 'visible')
    return
  }

  // Calculate total for selected group (for display only)
  let group_total = 0
  badges.forEach((badge) => {
    if (badge.student_group === group_name) {
      group_total += flt(badge.badge_points) || 0
    }
  })

  // Update display field with group total
  frm.doc.custom_total_badge_point = group_total
  frm.refresh_field('custom_total_badge_point')

  // Show the field after calculation is done
  frm
    .get_field('custom_total_badge_point')
    .$wrapper.css('visibility', 'visible')
}

frappe.ui.form.on('Student Guardian', {
  guardians_add: function (frm) {
    frm.fields_dict['guardians'].grid.get_field('guardian').get_query =
      function (doc) {
        let guardian_list = []
        if (!doc.__islocal) guardian_list.push(doc.guardian)
        $.each(doc.guardians, function (idx, val) {
          if (val.guardian) guardian_list.push(val.guardian)
        })
        return { filters: [['Guardian', 'name', 'not in', guardian_list]] }
      }
  },
})
