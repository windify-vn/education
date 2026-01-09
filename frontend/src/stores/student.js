import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createResource } from 'frappe-ui'

export const studentStore = defineStore('education-student', () => {
  const studentInfo = ref({})
  const currentProgram = ref({})
  const currentPrograms = ref([]) // All active programs
  const studentGroups = ref([])

  const student = createResource({
    url: 'education.education.api.get_student_info',
    onSuccess(info) {
      if (!info) {
        window.location.href = '/app/education'
      }
      currentProgram.value = info.current_program
      currentPrograms.value = info.current_programs || [] // All programs
      // remove from info
      delete info.current_program
      delete info.current_programs
      studentGroups.value = info.student_groups
      delete info.student_groups
      studentInfo.value = info
    },
    onError(err) {
      console.error(err)
      window.location.href = '/app/education'
    },
  })

  // const s = createDocumentResource({
  // 	doctype:"Student",
  // 	whitelist: {
  // 		'get_student_info': get_student_info
  // 	}
  // })

  function getStudentInfo() {
    return studentInfo
  }
  function getCurrentProgram() {
    return currentProgram
  }

  function getCurrentPrograms() {
    return currentPrograms
  }

  function getStudentGroups() {
    return studentGroups
  }

  return {
    student,
    studentInfo,
    currentProgram,
    currentPrograms,
    studentGroups,
    getStudentInfo,
    getCurrentProgram,
    getCurrentPrograms,
    getStudentGroups,
  }
})
