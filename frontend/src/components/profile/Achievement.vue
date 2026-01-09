<script setup>
import { useApi } from '@/composables/useApi'
import { GRADIENTS } from '@/constants/colors'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

defineEmits(['view-progress'])
const props = defineProps({
  studentName: {
    type: String,
    default: '',
  },
})
const { get } = useApi()

const isModalOpen = ref(false)
const selectedAchievement = ref(null)
const studentDetail = ref(null)
const studentBadge = ref(null)
const loadingStudent = ref(false)
const studentError = ref(null)

const progressMessages = [
  {
    text: 'Hãy bắt đầu hành trình chinh phục huy hiệu này! Mỗi đóng góp của bạn đều giúp cộng đồng học tập tốt hơn.',
    className: 'text-gray-700',
  },
  {
    text: 'Khởi đầu rất tốt! Bạn đã có những đóng góp đầu tiên – hãy tiếp tục để tiến gần hơn tới huy hiệu.',
    className: 'text-gray-700',
  },
  {
    text: 'Bạn đang đi đúng hướng! Những đóng góp của bạn đang tạo ra giá trị thực cho cộng đồng.',
    className: 'text-gray-700',
  },
  {
    text: 'Chỉ còn vài bước nữa thôi! Hãy tiếp tục chia sẻ và hoàn thiện để chạm tay vào huy hiệu này.',
    className: 'text-gray-700',
  },
  {
    text: 'Rất gần rồi! Chỉ còn một bước cuối cùng để bạn chính thức đạt được huy hiệu.',
    className: 'text-amber-600 font-semibold',
  },
  {
    text: '🎉 Chúc mừng bạn đã đạt được huy hiệu này! Cảm ơn bạn đã đóng góp tích cực và giúp cộng đồng phát triển tốt hơn mỗi ngày.',
    className: 'text-green-600 font-semibold',
  },
]

const progressDetail = computed(() => {
  const progress = selectedAchievement.value?.popup?.progress
  const current = progress?.current ?? 0
  const target = progress?.target ?? 5
  if (target <= 0) {
    return progressMessages[0]
  }
  const normalized = Math.max(
    0,
    Math.min(5, Math.round((current / target) * 5)),
  )
  return progressMessages[normalized]
})

async function fetchStudentProfile() {
  if (!props.studentName) {
    return null
  }

  loadingStudent.value = true
  studentError.value = null
  try {
    const data = await get(
      `/resource/Student/${encodeURIComponent(props.studentName)}`,
      { fields: JSON.stringify(['custom_list_badge']) },
    )
    studentDetail.value = data
    studentBadge.value = data?.data?.custom_list_badge ?? null
    return data
  } catch (error) {
    studentError.value = error
    console.error('Failed to load student detail', error)
    return null
  } finally {
    loadingStudent.value = false
  }
}

const openModal = (ach) => {
  selectedAchievement.value = ach
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  selectedAchievement.value = null
}

const handleKeydown = (event) => {
  if (event.key === 'Escape' && isModalOpen.value) {
    closeModal()
  }
}

onMounted(() => {
  fetchStudentProfile()
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})

watch(
  () => props.studentName,
  (newName, oldName) => {
    if (newName && newName !== oldName) {
      fetchStudentProfile()
    }
  },
  { immediate: true },
)

const mappedBadges = computed(() => {
  if (!Array.isArray(studentBadge.value) || studentBadge.value.length === 0)
    return []

  return studentBadge.value.map((badge) => {
    const criteriaHtml =
      badge?.badge_criteria ||
      badge?.badge_description ||
      `Huy hiệu: ${badge?.badge_name || badge?.badge || 'Chưa rõ'}`
    const criteriaList = [criteriaHtml]

    return {
      image:
        'https://education.windify.edu.vn' + badge?.badge_link_image ||
        'https://education.windify.edu.vn/files/robot-acedemy-52.png',
      title: badge?.badge_name || badge?.badge || 'Huy hiệu',
      description: badge?.badge_description || 'Huy hiệu từ hệ thống',
      studentGroup: badge?.student_group || null,
      popup: {
        badgeTitle: badge?.badge_name || badge?.badge || 'Huy hiệu',
        level: badge?.badge_level || 'N/A',
        points: Number(badge?.badge_points) || 0,
        summary: badge?.badge_description || 'Huy hiệu từ hệ thống',
        criteria: criteriaList,
        progress: { current: 0, target: 5 },
        studentGroup: badge?.student_group || null,
      },
    }
  })
})

const displayAchievements = computed(() => mappedBadges.value)
</script>

<template>
  <div class="overflow-hidden rounded-lg shadow-xl">
    <div
      class="relative text-white p-4"
      :style="{ background: GRADIENTS.primary }"
    >
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold">Huy hiệu</h3>
      </div>
    </div>

    <div class="p-4">
      <div
        class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-7 gap-4"
      >
        <button
          v-for="(ach, idx) in displayAchievements"
          :key="idx"
          type="button"
          class="rounded-lg border-2 border-dashed border-gray-300 p-4 flex flex-col items-center hover:border-primary-500 hover:shadow-lg transition"
          @click="openModal(ach)"
        >
          <figure>
            <img :src="ach.image" :alt="ach.title" />
          </figure>
          <h4
            class="mt-2 text-center text-xs text-gray-800 font-medium truncate w-full"
          >
            {{ ach.title }}
          </h4>
          <p
            class="mt-1 text-center text-[11px] text-gray-600 line-clamp-2"
            v-html="ach.description"
          ></p>
        </button>
      </div>
    </div>
  </div>

  <div
    v-if="isModalOpen && selectedAchievement"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
    role="dialog"
    aria-modal="true"
    @click.self="closeModal"
  >
    <div
      class="w-full max-w-[600px] rounded-lg md:rounded-2xl bg-white shadow-2xl overflow-hidden"
    >
      <div class="w-full max-h-[94svh] overflow-y-auto">
        <div
          class="relative h-[300px] max-h-[62vw] bg-gradient-to-br from-orange-300 via-orange-400 to-orange-500 flex items-center justify-center"
        >
          <figure class="h-full aspect-square">
            <img
              :src="selectedAchievement.image"
              :alt="selectedAchievement.title"
              class="h-full w-full object-cover drop-shadow-xl"
            />
          </figure>
          <button
            type="button"
            class="absolute right-3 top-3 h-9 w-9 rounded-full bg-white/80 text-gray-700 transition-all duration-300 hover:bg-white shadow flex items-center justify-center text-base font-semibold"
            @click="closeModal"
            aria-label="Đóng"
          >
            &times;
          </button>
        </div>

        <div class="p-6 space-y-4">
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <h4 class="text-xl font-semibold text-gray-900">
                {{ selectedAchievement.popup.badgeTitle }}
              </h4>
              <span
                v-if="selectedAchievement.popup.studentGroup"
                class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                style="
                  background-color: #fef3c7;
                  color: #92400e;
                  border: 1px solid #fcd34d;
                "
              >
                {{ selectedAchievement.popup.studentGroup }}
              </span>
            </div>
            <p
              class="mt-2 text-sm text-gray-600 leading-snug"
              v-html="selectedAchievement.popup.summary"
            ></p>
            <div class="mt-3 flex items-center gap-3 text-sm text-gray-700">
              <span
                class="flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1"
              >
                <span class="text-orange-500">◆</span> Level
                {{ selectedAchievement.popup.level }}
              </span>
              <span
                class="flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1"
              >
                <span class="text-amber-500">★</span>
                {{ selectedAchievement.popup.points }} điểm
              </span>
            </div>
          </div>

          <div
            class="rounded-xl bg-emerald-50 border border-emerald-200 px-4 py-3"
          >
            <p class="text-sm leading-snug" :class="progressDetail.className">
              {{ progressDetail.text }}
            </p>
          </div>

          <div class="rounded-xl border border-gray-200">
            <div class="border-b border-gray-200 px-4 py-3">
              <p class="font-semibold text-gray-900 flex items-center gap-2">
                <span class="size-5 text-green-500"
                  ><svg
                    width="100%"
                    height="100%"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M16.19 2H7.81C4.17 2 2 4.17 2 7.81V16.18C2 19.83 4.17 22 7.81 22H16.18C19.82 22 21.99 19.83 21.99 16.19V7.81C22 4.17 19.83 2 16.19 2ZM16.78 9.7L11.11 15.37C10.97 15.51 10.78 15.59 10.58 15.59C10.38 15.59 10.19 15.51 10.05 15.37L7.22 12.54C6.93 12.25 6.93 11.77 7.22 11.48C7.51 11.19 7.99 11.19 8.28 11.48L10.58 13.78L15.72 8.64C16.01 8.35 16.49 8.35 16.78 8.64C17.07 8.93 17.07 9.4 16.78 9.7Z"
                      fill="currentColor"
                    /></svg
                ></span>
                <span>Tiêu chí để đạt được huy hiệu</span>
              </p>
            </div>
            <div class="px-4 py-3 space-y-3">
              <div
                class="achievement-criteria"
                v-html="selectedAchievement.popup.criteria"
              ></div>

              <!-- <div class="space-y-2">
                <div class="flex justify-between text-sm text-gray-600">
                  <span>Tiến độ hoàn thành</span>
                  <span>{{ selectedAchievement.popup.progress.current }} / {{ selectedAchievement.popup.progress.target }}</span>
                </div>
                <div class="h-3 w-full rounded-full bg-gray-100">
                  <div
                    class="h-3 rounded-full bg-gradient-to-r from-green-400 to-green-500"
                    :style="{ width: `${(selectedAchievement.popup.progress.current / selectedAchievement.popup.progress.target) * 100}%` }"
                  />
                </div>
              </div> -->
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.achievement-criteria :deep(.ql-editor) {
  color: #374151;
  font-size: 0.875rem;
  line-height: 1.75;
}

.achievement-criteria :deep(.ql-editor p) {
  margin-bottom: 0.5rem;
}

.achievement-criteria :deep(.ql-editor p:last-child) {
  margin-bottom: 0;
}

.achievement-criteria :deep(.ql-editor ul) {
  list-style: none;
  padding-left: 0;
  margin: 0.5rem 0;
}

.achievement-criteria :deep(.ql-editor li) {
  position: relative;
  padding-left: 1rem;
  color: #374151;
  margin-bottom: 0.375rem;
}

.achievement-criteria :deep(.ql-editor li[data-list='bullet']) {
  padding-left: 1rem;
}

.achievement-criteria :deep(.ql-editor li[data-list='bullet']::before) {
  content: '•';
  position: absolute;
  left: 0;
  color: #6b7280;
  font-weight: 700;
}

.achievement-criteria :deep(.ql-editor li.ql-indent-1) {
  padding-left: 2rem;
}

.achievement-criteria :deep(.ql-editor li.ql-indent-1::before) {
  left: 1rem;
}

.achievement-criteria :deep(.ql-editor .ql-ui) {
  display: none;
}

.achievement-criteria :deep(.ql-editor strong) {
  font-weight: 600;
  color: #111827;
}
</style>
