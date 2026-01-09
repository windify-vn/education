<script setup>
import { onMounted, reactive, ref, watchEffect } from 'vue'
import { createResource } from 'frappe-ui'
import {
  ArrowDown,
  ArrowUp,
  BookOpen,
  Clock,
  Users,
  CheckCircle,
  Circle,
  Play,
  Eye,
} from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { COLORS, GRADIENTS } from '@/constants/colors'

const props = defineProps({
  studentName: { type: String, default: '' },
  title: { type: String, default: 'Chương trình học đang tham gia' },
  openAll: { type: Boolean, default: false },
})

const emit = defineEmits(['programs-loaded'])

const router = useRouter()
const siteUrl = window.location.origin

const programLoading = reactive({}) // program -> boolean
const programs = ref([])
const opened = reactive(new Set()) // lưu trạng thái mở theo program
const programCourses = reactive({}) // program -> [courseName]
const programEnrollmentMap = reactive({}) // program -> program enrollment doc name
const programDetail = reactive({}) // programName -> doc
const courseDetail = reactive({}) // courseName -> doc
const topicDetail = reactive({}) // topicName -> doc
const topicsFetched = reactive(new Set()) // cache fetched topics per course

function isExpanded(programName) {
  if (props.openAll) {
    opened.add(programName)
    if (!programCourses[programName]) {
      loadProgramCourses(programName)
    }
    return true
  } else {
    return opened.has(programName)
  }
}

function toggleProgram(programName) {
  if (opened.has(programName)) {
    opened.delete(programName)
  } else {
    opened.add(programName)
    if (!programCourses[programName]) {
      loadProgramCourses(programName)
    }
  }
}

function handleProgramClick(programName) {
  router.push(`/program/${programName}`)
}

function handleCourseClick(programName, courseName) {
  router.push(`/program/${programName}/${courseName}`)
}

function handleTopicClick(programName, courseName, topicName) {
  router.push(`/program/${programName}/${courseName}/${topicName}`)
}

function onButtonEnter(e) {
  e.target.style.backgroundColor = COLORS.primary
  e.target.style.color = 'white'
}

function onButtonLeave(e) {
  e.target.style.backgroundColor = 'transparent'
  e.target.style.color = COLORS.primary
}

defineExpose({ toggleProgram })

function loadPrograms() {
  if (!props.studentName) return
  createResource({
    url: 'education.education.api.get_student_programs',
    method: 'POST',
    params: { student: props.studentName },
    onSuccess: async (res) => {
      Object.keys(programEnrollmentMap).forEach(
        (key) => delete programEnrollmentMap[key],
      )
      programs.value = res || []
      programs.value.forEach((p) => {
        if (p?.program) {
          programEnrollmentMap[p.program] = p.name
        }
      })
      await Promise.all(programs.value.map((p) => loadProgramDetail(p.program)))
      // Emit programs để component cha có thể sử dụng
      emit('programs-loaded', programs.value)
    },
    onError: (err) => {
      console.error(err)
      programs.value = []
    },
  }).submit()
}

function loadProgramDetail(programName) {
  return new Promise((resolve) => {
    createResource({
      url: 'frappe.client.get',
      method: 'POST',
      params: { doctype: 'Program', name: programName },
      onSuccess: (doc) => {
        programDetail[programName] = doc
        resolve()
      },
      onError: () => {
        programDetail[programName] = []
        resolve()
      },
    }).submit()
  })
}

function loadProgramCourses(programName) {
  programLoading[programName] = true
  const enrollmentName = programEnrollmentMap[programName]
  createResource({
    url: 'education.education.api.get_course_list_based_on_program',
    method: 'POST',
    params: {
      program_name: programName,
      program_enrollment: enrollmentName,
      student: props.studentName || undefined,
    },
    onSuccess: async (res) => {
      const courseList = Array.isArray(res) ? res : []
      programCourses[programName] = courseList
      await Promise.all(
        courseList.map((c) =>
          topicsFetched.has(c) ? Promise.resolve() : loadCourseDetail(c),
        ),
      )
      programLoading[programName] = false
    },
    onError: () => {
      programCourses[programName] = []
      programLoading[programName] = false
    },
  }).submit()
}

function loadCourseDetail(courseName) {
  return new Promise((resolve) => {
    createResource({
      url: 'frappe.client.get',
      method: 'POST',
      params: { doctype: 'Course', name: courseName },
      onSuccess: async (doc) => {
        courseDetail[courseName] = doc
        topicsFetched.add(courseName)
        await Promise.all(
          doc.topics.map((t) =>
            topicsFetched.has(t)
              ? Promise.resolve()
              : getTopicDetail(t.topic_name),
          ),
        )
        resolve()
      },
      onError: () => {
        courseDetail[courseName] = []
        topicsFetched.delete(courseName)
        resolve()
      },
    }).submit()
  })
}

function getTopicDetail(topicName) {
  return new Promise((resolve) => {
    createResource({
      url: 'frappe.client.get',
      method: 'POST',
      params: { doctype: 'Topic', name: topicName },
      onSuccess: (doc) => {
        topicDetail[topicName] = doc
        topicsFetched.add(topicName)
        resolve()
      },
      onError: () => {
        topicDetail[topicName] = []
        topicsFetched.delete(topicName)
        resolve()
      },
    }).submit()
  })
}

onMounted(() => {
  loadPrograms()
})

// Nếu prop studentName thay đổi (edge-case), tự tải lại
watchEffect(() => {
  if (props.studentName && programs.value.length === 0) {
    loadPrograms()
  }
})

// Removed openAllTrigger/closeAllTrigger handlers per request
</script>

<template>
  <div class="overflow-hidden rounded-lg shadow-xl bg-white">
    <!-- Header -->
    <div
      class="relative text-white p-3 md:p-6"
      :style="{ background: GRADIENTS.primary }"
    >
      <div
        class="flex flex-col md:flex-row items-start md:items-center justify-between md:justify-between gap-3"
      >
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-white/20 rounded-lg">
            <BookOpen class="md:size-6 size-4" />
          </div>
          <div>
            <h3 class="md:text-xl text-base font-bold">{{ title }}</h3>
            <p class="md:text-sm text-xs text-white/90 mt-1">
              Lộ trình học tập của bạn
            </p>
          </div>
        </div>
        <div class="flex items-center space-x-2 ml-[44px] md:ml-[56px]">
          <div class="md:text-2xl text-xl font-bold">{{ programs.length }}</div>
          <div class="md:text-sm text-xs text-white/80">Chương trình</div>
        </div>
      </div>
    </div>

    <!-- Timeline Content -->
    <div class="p-3 md:p-6">
      <div v-if="programs.length" class="space-y-8">
        <div
          v-for="(p, programIndex) in programs"
          :key="p.name || p.program"
          class="relative"
        >
          <!-- Timeline Line -->
          <div
            v-if="programIndex < programs.length - 1"
            :style="{
              background: `linear-gradient(to bottom, ${COLORS.primary}, ${COLORS.primaryLight})`,
              opacity: 0.3,
            }"
            class="absolute left-3 md:left-6 top-16 w-0.5 h-full"
          ></div>

          <!-- Program Card -->
          <div class="relative">
            <!-- Program Content -->
            <div
              class="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden"
            >
              <!-- Program Header -->
              <button
                class="w-full flex items-center justify-between p-3 md:p-6 text-left hover:bg-gray-50 transition-colors"
                @click="toggleProgram(p.program)"
              >
                <div class="flex-1 min-w-0">
                  <div
                    class="flex flex-col sm:flex-row sm:items-center gap-2 mb-2"
                  >
                    <h4
                      @click.stop="handleProgramClick(p.program)"
                      :style="{ color: 'inherit' }"
                      class="md:text-lg text-sm font-semibold text-gray-900 transition-colors cursor-pointer"
                      @mouseenter="$event.target.style.color = COLORS.primary"
                      @mouseleave="$event.target.style.color = 'inherit'"
                    >
                      {{ p.program }}
                    </h4>
                    <span
                      :style="{ background: GRADIENTS.primary }"
                      class="px-2 py-0.5 text-white text-2xs font-medium rounded-full whitespace-nowrap w-fit"
                    >
                      Chương trình {{ programIndex + 1 }}
                    </span>
                  </div>
                  <p class="md:text-sm text-xs text-gray-600 mb-3">
                    Nhấn để xem chi tiết khóa học và nội dung
                  </p>

                  <!-- Program Stats -->
                  <div
                    class="flex items-center space-x-4 md:space-x-6 md:text-sm text-xs text-gray-500"
                  >
                    <div class="flex items-center space-x-1">
                      <BookOpen class="md:size-4 size-3" />
                      <span
                        >{{ programCourses[p.program]?.length || 0 }} khóa
                        học</span
                      >
                    </div>
                    <div class="flex items-center space-x-1">
                      <Clock class="md:size-4 size-3" />
                      <span>Thời gian linh hoạt</span>
                    </div>
                  </div>
                </div>

                <!-- Toggle Button -->
                <div
                  class="ml-2 md:ml-4 p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors flex items-center justify-center flex-shrink-0"
                >
                  <ArrowUp
                    v-if="isExpanded(p.program)"
                    :style="{ color: COLORS.primary }"
                    class="md:size-5 size-4"
                  />
                  <ArrowDown
                    v-else
                    :style="{ color: COLORS.primary }"
                    class="md:size-5 size-4"
                  />
                </div>
              </button>

              <!-- Expanded Content -->
              <div
                v-if="isExpanded(p.program)"
                class="border-t border-gray-100"
              >
                <!-- Loading State -->
                <div
                  v-if="programLoading[p.program]"
                  class="p-3 md:p-6 text-center"
                >
                  <div class="inline-flex items-center space-x-2 text-gray-600">
                    <div
                      class="animate-spin rounded-full h-4 w-4 border-2 border-t-transparent"
                      :style="{ borderColor: COLORS.primary }"
                    ></div>
                    <span>Đang tải danh sách khóa học...</span>
                  </div>
                </div>

                <!-- Courses Timeline -->
                <div
                  v-else-if="programCourses[p.program]?.length"
                  class="p-3 md:p-6"
                >
                  <div class="space-y-6">
                    <div
                      v-for="(courseName, courseIndex) in programCourses[
                        p.program
                      ]"
                      :key="courseName"
                      class="relative"
                    >
                      <!-- Course Timeline Line -->
                      <div
                        v-if="
                          courseIndex < programCourses[p.program].length - 1
                        "
                        class="absolute left-3 md:left-4 top-12 w-0.5 h-full bg-gray-200"
                      ></div>

                      <!-- Course Card -->
                      <div class="relative">
                        <!-- Course Content -->
                        <div
                          class="bg-gray-50 rounded-lg p-3 md:p-4 hover:bg-gray-100 transition-colors"
                        >
                          <div
                            class="flex flex-col md:flex-row items-start justify-between gap-4"
                          >
                            <!-- Course Image -->
                            <div
                              v-if="
                                courseDetail[courseName]?.hero_image?.length > 0
                              "
                              class="aspect-video md:h-48 h-36 rounded-md overflow-hidden flex-shrink-0 shadow-md ring-2"
                              :style="{ ringColor: COLORS.secondary }"
                            >
                              <img
                                :src="`${siteUrl}${courseDetail[courseName].hero_image}`"
                                alt="Course Image"
                                class="w-full h-full object-cover"
                              />
                            </div>

                            <div class="flex flex-col flex-1 gap-4 w-full">
                              <!-- Course Name and Description -->
                              <div class="flex flex-col gap-2">
                                <h5
                                  :style="{ color: 'inherit' }"
                                  class="md:text-lg text-base font-semibold text-gray-900 mb-1 cursor-pointer transition-colors"
                                  @mouseenter="
                                    $event.target.style.color = COLORS.primary
                                  "
                                  @mouseleave="
                                    $event.target.style.color = 'inherit'
                                  "
                                  @click="
                                    handleCourseClick(p.program, courseName)
                                  "
                                >
                                  {{ courseName }}
                                </h5>
                                <p
                                  v-if="courseDetail[courseName]?.description"
                                  class="text-sm text-gray-600 line-clamp-2"
                                >
                                  {{ courseDetail[courseName].description }}
                                </p>
                              </div>
                              <!-- Topics List -->
                              <div
                                v-if="courseDetail[courseName]?.topics?.length"
                                class="flex-1"
                              >
                                <div class="flex items-center space-x-2 mb-3">
                                  <Play
                                    :style="{ color: COLORS.primary }"
                                    class="w-4 h-4"
                                  />
                                  <span
                                    class="text-sm font-medium text-gray-700"
                                    >Nội dung khóa học</span
                                  >
                                </div>

                                <div
                                  class="grid grid-cols-1 md:grid-cols-2 gap-2"
                                >
                                  <div
                                    v-for="(topic, topicIndex) in courseDetail[
                                      courseName
                                    ].topics"
                                    :key="topic.topic_name"
                                    class="flex items-center space-x-2 p-2 bg-white rounded-md border border-gray-200 transition-colors cursor-pointer"
                                    :style="{ borderColor: 'inherit' }"
                                    @mouseenter="
                                      $event.currentTarget.style.borderColor =
                                        COLORS.primary
                                    "
                                    @mouseleave="
                                      $event.currentTarget.style.borderColor =
                                        'inherit'
                                    "
                                    @click="
                                      handleTopicClick(
                                        p.program,
                                        courseName,
                                        topic.topic_name,
                                      )
                                    "
                                  >
                                    <div class="flex-shrink-0">
                                      <!-- <Circle v-if="topicIndex < 3" :style="{ color: COLORS.primary }" class="w-3 h-3 fill-current" /> -->
                                      <CheckCircle
                                        class="w-3 h-3 text-green-500"
                                      />
                                    </div>
                                    <span
                                      class="text-sm text-gray-700 truncate hover:text-primary"
                                      >{{ topic.topic_name }}</span
                                    >
                                  </div>
                                </div>

                                <!-- Show More Topics
                                <div v-if="courseDetail[courseName].topics.length > 6" class="mt-2 text-center">
                                  <button :style="{ color: COLORS.primary }" class="text-xs hover:underline">
                                    Xem thêm {{ courseDetail[courseName].topics.length - 6 }} chủ đề khác
                                  </button>
                                </div> -->
                              </div>

                              <!-- No Topics -->
                              <div
                                v-else
                                class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md"
                              >
                                <p class="text-sm text-yellow-700 text-center">
                                  Chưa có bài học nào được thêm vào khóa học này
                                </p>
                              </div>

                              <div
                                class="flex items-center space-x-2 justify-end"
                              >
                                <button
                                  :style="{
                                    color: COLORS.primary,
                                    borderColor: COLORS.primary,
                                  }"
                                  class="text-xs border rounded-md px-4 py-2 transition-colors flex items-center space-x-2"
                                  @mouseenter="onButtonEnter"
                                  @mouseleave="onButtonLeave"
                                  @click="
                                    handleCourseClick(p.program, courseName)
                                  "
                                >
                                  <Eye class="md:size-4 size-3" />
                                  <span>Xem chi tiết</span>
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- No Courses -->
                <div v-else class="p-6 text-center">
                  <div class="text-gray-500">
                    <BookOpen class="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p class="text-sm">
                      Chưa có khóa học nào trong chương trình này
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <div class="text-gray-500">
          <BookOpen class="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">
            Chưa có chương trình nào
          </h3>
          <p class="text-sm">Bạn chưa được đăng ký vào chương trình học nào</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom styles for timeline */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Smooth transitions for timeline elements */
.timeline-item {
  transition: all 0.3s ease;
}

.timeline-item:hover {
  transform: translateY(-2px);
}

/* Custom scrollbar for better UX */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(
    135deg,
    var(--color-primary),
    var(--color-primary-light)
  );
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #e04a1f, #e0814a);
}

/* Animation for loading spinner */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Hover effects for interactive elements */
.hover-lift:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(242, 90, 35, 0.15);
}

/* Gradient text effect */
.gradient-text {
  background: linear-gradient(
    135deg,
    var(--color-primary),
    var(--color-primary-light)
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
