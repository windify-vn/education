<script setup>
import { onMounted, reactive } from 'vue'
import { createResource } from 'frappe-ui'
import CourseDetailHeader from '@/components/course/CourseDetailHeader.vue'
import TopicsTimeline from '../components/course/TopicsTimeline.vue'
import { useRoute, useRouter } from 'vue-router'
import { COLORS, GRADIENTS } from '@/constants/colors'

const route = useRoute()
const router = useRouter()

const courseName = route.params.courseName
const programName = route.params.programName
const siteUrl = window.location.origin
const courseDetail = reactive({})

function loadCourseDetail(courseName) {
  return new Promise((resolve) => {
    createResource({
      url: 'frappe.client.get',
      method: 'POST',
      params: { doctype: 'Course', name: courseName },
      onSuccess: async (doc) => {
        courseDetail[courseName] = doc
        console.log('Course Detail:', courseDetail[courseName])
        resolve()
      },
      onError: () => {
        courseDetail[courseName] = []
        resolve()
      },
    }).submit()
  })
}

function handleTopicClick(programName, courseName, topicName) {
  router.push(`/program/${programName}/${courseName}/${topicName}`)
}

function goBack() {
  router.push('/program')
}

onMounted(async () => {
  await loadCourseDetail(courseName)
})
</script>

<template>
  <div class="p-5 space-y-6">
    <CourseDetailHeader
      :courseDoc="courseDetail[courseName]"
      :courseName="courseName"
      :programName="programName"
      :siteUrl="siteUrl"
      :gradients="GRADIENTS"
      :colors="COLORS"
      :showBackButton="true"
      @back="goBack"
    />

    <!-- Topics Timeline -->
    <TopicsTimeline
      :courseDetail="courseDetail[courseName]"
      :courseName="courseName"
      :siteUrl="siteUrl"
      @topicClick="
        (topicName) => handleTopicClick(programName, courseName, topicName)
      "
    />
  </div>
</template>
