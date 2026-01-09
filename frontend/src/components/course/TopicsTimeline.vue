<script setup>
import { reactive, watchEffect } from 'vue'
import { createResource } from 'frappe-ui'
import { Circle, CheckCircle, ArrowDown, ArrowUp, Play } from 'lucide-vue-next'
import { COLORS } from '@/constants/colors'

const props = defineProps({
  courseDetail: {
    type: Object,
    required: true
  },
  courseName: {
    type: String,
    required: true
  },
  siteUrl: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['topicClick'])

const topicDetail = reactive({})
const topicsFetched = reactive(new Set())
const expandedTopics = reactive(new Set())

function toggleTopic(topicName) {
  if (expandedTopics.has(topicName)) {
    expandedTopics.delete(topicName)
  } else {
    expandedTopics.add(topicName)
  }
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
        topicDetail[topicName] = {}
        topicsFetched.delete(topicName)
        resolve()
      },
    }).submit()
  })
}

function handleTopicClick(topicName) {
  emit('topicClick', topicName)
}

watchEffect(async () => {
  if (props.courseDetail && Array.isArray(props.courseDetail.topics)) {
    await Promise.all(
      props.courseDetail.topics.map((t) =>
        topicsFetched.has(t.topic_name) ? Promise.resolve() : getTopicDetail(t.topic_name)
      )
    )
  }
})
</script>

<template>
  <div class="overflow-hidden rounded-lg shadow-xl bg-white">
    <div class="p-3 md:p-6">
      <div class="flex items-center space-x-2 mb-4">
        <Play :style="{ color: COLORS.primary }" class="md:size-5 size-4" />
        <h4 class="md:text-lg text-base font-semibold">Nội dung chi tiết bài học:</h4>
      </div>

      <div v-if="Array.isArray(courseDetail?.topics) && courseDetail.topics.length" class="relative flex gap-5">
        <div v-if="courseDetail.topics.length > 1" class="w-[2px] my-2 ml-1"
          style="background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-primary-light) 100%); border-radius: 0.25rem;">
        </div>
        <div class="space-y-4 w-full">
          <div v-for="(t, idx) in courseDetail.topics" :key="t.topic_name" class="relative">
            <!-- Topic Card -->
            <div class="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
              <button
                class="w-full flex items-center justify-between p-3 md:p-4 text-left hover:bg-gray-100 transition-colors"
                @click="toggleTopic(t.topic_name)">
                <div class="flex items-center space-x-2">
                  <!-- <Circle v-if="idx < 3" :style="{ color: COLORS.primary }" class="md:size-3 size-2 fill-current" /> -->
                  <CheckCircle class="md:size-3 size-2 text-green-500" />
                  <div @click.stop="handleTopicClick(t.topic_name)"
                    class="md:text-base text-sm font-semibold text-gray-900 flex-1 cursor-pointer hover:underline hover:text-[var(--color-primary)]">
                    {{ topicDetail[t.topic_name]?.topic_name || t.topic_name }}
                  </div>
                </div>
                <span class="ml-4 p-2 rounded-lg bg-white border border-gray-200">
                  <ArrowUp v-if="expandedTopics.has(t.topic_name)" :style="{ color: COLORS.primary }"
                    class="md:size-4 size-3" />
                  <ArrowDown v-else :style="{ color: COLORS.primary }" class="md:size-4 size-3" />
                </span>
              </button>

              <div v-show="expandedTopics.has(t.topic_name)" class="p-3 md:p-4 border-t border-gray-200">
                <div class="flex flex-col gap-4">
                  <div class="flex lg:flex-row flex-col gap-4">
                    <!-- Hero Image -->
                    <div v-if="topicDetail[t.topic_name]?.hero_image"
                      class="aspect-video md:h-48 h-36 rounded-md overflow-hidden shadow-md ring-2"
                      :style="{ ringColor: COLORS.secondary }">
                      <img :src="`${siteUrl}${topicDetail[t.topic_name].hero_image}`" alt="Topic Image"
                        class="w-full h-full object-cover" />
                    </div>
                    <!-- Placeholder image -->
                    <div v-else class="aspect-video md:h-48 h-36 rounded-md overflow-hidden shadow-md ring-2"
                      :style="{ ringColor: COLORS.secondary }">
                      <img
                        src="https://www.placeholderimage.online/placeholder/420/310/ededed/e6e6e6?text=Topic&font=Poppins.webp"
                        alt="Topic Image" class="w-full h-full object-cover" />
                    </div>

                    <div class="flex flex-col gap-4 flex-1">
                      <!-- Description -->
                      <p v-if="topicDetail[t.topic_name]?.description"
                        class="text-2xs md:text-sm text-gray-600 text-justify">
                        {{ topicDetail[t.topic_name].description }}
                      </p>
                      <p v-else class="text-2xs md:text-sm text-gray-600 text-justify">
                        Không có mô tả cho bài học này
                      </p>
                    </div>
                  </div>
                  <!-- Button to go to topic detail -->
                  <div class="flex justify-end items-start h-full">
                    <button :style="{ color: COLORS.primary, borderColor: COLORS.primary }"
                      class="text-xs border rounded-[0.5rem] px-2 py-1 transition-colors flex items-center space-x-2"
                      @mouseenter="$event.target.style.backgroundColor = COLORS.primary; $event.target.style.color = 'white'"
                      @mouseleave="$event.target.style.backgroundColor = 'transparent'; $event.target.style.color = COLORS.primary"
                      @click="handleTopicClick(t.topic_name)">
                      <span>Xem chi tiết</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center text-gray-500">
        Chưa có chủ đề nào cho bài học này.
      </div>
    </div>
  </div>
</template>