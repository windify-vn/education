<script setup>
import { onMounted, reactive, ref, watchEffect, computed } from 'vue'
import { createResource } from 'frappe-ui'
import TopicDetailItem from '../components/course/TopicDetailItem.vue'
import PreviewVideo from '@/components/Preview/PreviewVideo.vue'
import PreviewDocument from '@/components/Preview/PreviewDocument.vue'
import QuizContent from '../components/course/QuizContent.vue'
import {
  ArrowLeft,
  Link as LinkIcon,
  Eye,
  X,
  Play,
  FileText,
  HelpCircle,
} from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import { COLORS } from '@/constants/colors'
import HomeworkSection from '../components/homework/HomeworkSection.vue'

const route = useRoute()
const router = useRouter()
const topicName = route.params.topicName
const courseName = route.params.courseName
const programName = route.params.programName
const siteUrl = window.location.origin

const topicDetail = reactive({})
const contentDetail = reactive({})
const loadingContentKeys = reactive(new Set())
const expandedContentKeys = reactive(new Set())
const expandedDocumentIndex = ref(null)

const safeDocuments = computed(() => {
  const docs = topicDetail[topicName]?.custom_topic_document
  if (!Array.isArray(docs)) return []
  return docs.filter((d) => d && typeof d === 'object')
})

function keyForContent(topicName, index) {
  return `${topicName}:${index}`
}

function toggleContentDetail(topicName, index) {
  const k = keyForContent(topicName, index)
  if (expandedContentKeys.has(k)) {
    expandedContentKeys.delete(k)
  } else {
    expandedContentKeys.add(k)
  }
}

function toggleDocumentPreviewByIndex(index) {
  expandedDocumentIndex.value =
    expandedDocumentIndex.value === index ? null : index
  if (expandedDocumentIndex.value !== null) {
    setTimeout(() => {
      const previewElement = document.querySelector(
        `[data-document-preview-index="${expandedDocumentIndex.value}"]`,
      )
      if (previewElement) {
        previewElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }, 100)
  }
}

function contentTypeMeta(type) {
  const t = (type || '').toLowerCase()
  if (t === 'video') {
    return {
      label: 'Video',
      classes:
        'bg-orange-50 text-[var(--color-primary)] border border-[var(--color-primary)]/30',
      icon: 'Film',
    }
  }
  if (t === 'article') {
    return {
      label: 'Article',
      classes: 'bg-blue-50 text-blue-600 border border-blue-200',
      icon: 'FileText',
    }
  }
  if (t === 'quiz') {
    return {
      label: 'Quiz',
      classes: 'bg-green-50 text-green-700 border border-green-200',
      icon: 'HelpCircle',
    }
  }
  return {
    label: type || 'Other',
    classes: 'bg-gray-100 text-gray-700 border border-gray-200',
    icon: 'FileText',
  }
}

function loadTopicContentDetail(item, topicName, index) {
  const k = keyForContent(topicName, index)
  if (contentDetail[k] || loadingContentKeys.has(k)) return

  loadingContentKeys.add(k)
  createResource({
    url: 'frappe.client.get',
    method: 'POST',
    params: { doctype: item.content_type, name: item.content },
    onSuccess: (res) => {
      contentDetail[k] = res?.message || res
      loadingContentKeys.delete(k)
    },
    onError: () => {
      loadingContentKeys.delete(k)
    },
  }).submit()
}

function toggleAndLoadContent(topicName, index, item) {
  toggleContentDetail(topicName, index)
  const k = keyForContent(topicName, index)
  if (expandedContentKeys.has(k)) {
    loadTopicContentDetail(item, topicName, index)
    setTimeout(() => {
      const previewElement = document.querySelector(`[data-preview-key="${k}"]`)
      if (previewElement) {
        previewElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }, 100)
  }
}

function loadTopicDetail(topicName) {
  return new Promise((resolve) => {
    createResource({
      url: 'frappe.client.get',
      method: 'POST',
      params: { doctype: 'Topic', name: topicName },
      onSuccess: (doc) => {
        topicDetail[topicName] = doc
        resolve()
      },
      onError: () => {
        topicDetail[topicName] = {}
        resolve()
      },
    }).submit()
  })
}

function goBack() {
  router.push(`/program/${programName}/${courseName}`)
}

onMounted(async () => {
  await loadTopicDetail(topicName)
})
</script>

<template>
  <div class="p-5 space-y-6">
    <!-- Header with back button -->
    <div
      class="flex items-center space-x-4 mb-6 p-4 rounded-lg"
      style="
        background: linear-gradient(
          135deg,
          var(--color-primary) 0%,
          var(--color-primary-light) 100%
        );
      "
    >
      <button
        @click="goBack"
        class="flex items-center space-x-2 text-white hover:text-gray-200 transition-colors"
      >
        <ArrowLeft class="size-4" />
        <span class="text-sm hidden sm:inline">Quay lại</span>
      </button>
      <div class="h-4 w-px bg-white/30"></div>
      <div>
        <h1 class="text-lg font-semibold text-white">
          {{ topicDetail[topicName]?.topic_name || topicName }}
        </h1>
        <p class="text-sm text-white/90">
          {{ courseName }} - {{ programName }}
        </p>
      </div>
    </div>

    <!-- Topic Hero Section -->
    <div
      v-if="topicDetail[topicName]"
      class="grid grid-cols-1 lg:grid-cols-3 gap-4"
    >
      <div class="col-span-3 grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div
          class="col-span-3 lg:col-span-2 overflow-hidden rounded-lg shadow-xl bg-white order-2 lg:order-1"
        >
          <div class="p-3 md:p-6 border-b border-gray-200">
            <!-- Topic Document -->
            <div
              v-if="
                Array.isArray(topicDetail[topicName]?.custom_topic_document) &&
                safeDocuments.length
              "
              class="mb-6"
            >
              <h3 class="md:text-lg text-base font-semibold mb-2">
                Tài liệu học tập
              </h3>
              <div class="grid grid-cols-1 gap-3">
                <div
                  v-for="(doc, idx) in safeDocuments"
                  :key="doc.name || idx"
                  class="p-4 bg-white rounded-lg border border-gray-200 transition-colors"
                  :style="{ borderColor: 'inherit' }"
                >
                  <div class="flex items-center justify-between gap-3">
                    <div class="flex items-center gap-3 overflow-hidden">
                      <div class="pt-0.5">
                        <LinkIcon
                          :style="{ color: COLORS.primary }"
                          class="size-4"
                        />
                      </div>
                      <div class="min-w-0 flex gap-1 items-center">
                        <h3
                          class="text-2xs md:text-sm font-semibold text-gray-900 truncate"
                        >
                          {{ doc.title || 'Tài liệu' }}
                        </h3>
                        <span class="text-2xs text-gray-500">-</span>
                        <p
                          v-if="doc?.document_file"
                          :href="`${siteUrl}${doc.document_file}`"
                          target="_blank"
                          :style="{ color: COLORS.primary }"
                          class="text-2xs hover:underline truncate"
                        >
                          {{ (doc?.document_file || '').split('/').pop() }}
                        </p>
                        <div v-else class="text-xs text-gray-400">
                          Không có file đính kèm
                        </div>
                      </div>
                    </div>

                    <button
                      v-if="doc?.document_file"
                      :style="{
                        color: COLORS.primary,
                        borderColor: COLORS.primary,
                      }"
                      class="text-2xs md:text-xs border rounded px-2 py-1 transition-colors flex items-center gap-1"
                      @click="toggleDocumentPreviewByIndex(idx)"
                    >
                      <Eye
                        v-if="expandedDocumentIndex !== idx"
                        class="size-3"
                      />
                      <X v-else class="size-3" />
                      {{ expandedDocumentIndex === idx ? 'Đóng' : 'Xem' }}
                    </button>
                  </div>

                  <!-- Inline Preview per document -->
                  <div
                    v-if="doc?.document_file && expandedDocumentIndex === idx"
                    :data-document-preview-index="idx"
                    class="mt-3 w-full md:col-span-2"
                  >
                    <PreviewDocument
                      :url="doc?.document_file"
                      :title="(doc?.document_file || '').split('/').pop()"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Topic Content -->
            <div
              v-if="
                Array.isArray(topicDetail[topicName]?.topic_content) &&
                topicDetail[topicName].topic_content.length
              "
            >
              <h3 class="md:text-lg text-base font-semibold mb-2">
                Nội dung bài học
              </h3>
              <div class="grid grid-cols-1 gap-4">
                <TopicDetailItem
                  v-for="(item, i) in topicDetail[topicName].topic_content"
                  :key="i"
                  :topic="item"
                  :topicName="topicName"
                  :index="i"
                  :dataKey="keyForContent(topicName, i)"
                  :expanded="
                    expandedContentKeys.has(keyForContent(topicName, i))
                  "
                  :colors="COLORS"
                  @toggle="() => toggleAndLoadContent(topicName, i, item)"
                >
                  <template #default>
                    <template
                      v-if="loadingContentKeys.has(keyForContent(topicName, i))"
                    >
                      <div class="flex items-center justify-center py-8">
                        <div class="text-gray-500">Đang tải nội dung...</div>
                      </div>
                    </template>
                    <template v-else>
                      <template
                        v-if="
                          contentTypeMeta(item.content_type).label === 'Video'
                        "
                      >
                        <PreviewVideo
                          :url="contentDetail[keyForContent(topicName, i)]?.url"
                        />
                      </template>
                      <template
                        v-else-if="
                          contentTypeMeta(item.content_type).label === 'Article'
                        "
                      >
                        <div class="space-y-4">
                          <div class="text-lg font-semibold text-gray-900">
                            {{
                              contentDetail[keyForContent(topicName, i)]
                                ?.title || 'Bài viết'
                            }}
                          </div>
                          <div class="text-sm text-gray-500">
                            <span
                              v-if="
                                contentDetail[keyForContent(topicName, i)]
                                  ?.author
                              "
                              >Tác giả:
                              {{
                                contentDetail[keyForContent(topicName, i)]
                                  ?.author
                              }}</span
                            >
                            <span
                              v-if="
                                contentDetail[keyForContent(topicName, i)]
                                  ?.publish_date
                              "
                            >
                              ·
                              {{
                                contentDetail[keyForContent(topicName, i)]
                                  ?.publish_date
                              }}</span
                            >
                          </div>
                          <div
                            class="prose max-w-none"
                            v-html="
                              contentDetail[keyForContent(topicName, i)]
                                ?.content || 'Chưa có nội dung bài viết.'
                            "
                          ></div>
                        </div>
                      </template>
                      <template
                        v-else-if="
                          contentTypeMeta(item.content_type).label === 'Quiz'
                        "
                      >
                        <QuizContent
                          :content="contentDetail[keyForContent(topicName, i)]"
                        />
                      </template>
                      <template v-else>
                        <div
                          class="p-4 bg-gray-50 border border-gray-200 rounded-lg"
                        >
                          <div class="text-lg font-semibold text-gray-800">
                            {{
                              contentDetail[keyForContent(topicName, i)]
                                ?.title || 'Nội dung'
                            }}
                          </div>
                        </div>
                      </template>
                    </template>
                  </template>
                </TopicDetailItem>
              </div>
            </div>

            <!-- No content message -->
            <div v-else class="text-center py-8 text-gray-500">
              <FileText class="size-12 mx-auto mb-3 text-gray-400" />
              <p>Chưa có nội dung cho bài học này</p>
            </div>
          </div>
        </div>
        <div
          class="col-span-3 lg:col-span-1 overflow-hidden rounded-lg shadow-xl bg-white order-1 lg:order-2"
        >
          <div class="p-3 md:p-6 border-b border-gray-200">
            <!-- Hero Image -->
            <div
              v-if="topicDetail[topicName]?.hero_image"
              class="aspect-video rounded-md overflow-hidden shadow-md ring-2 mb-6"
              :style="{ ringColor: COLORS.secondary }"
            >
              <img
                :src="`${siteUrl}${topicDetail[topicName].hero_image}`"
                alt="Topic Image"
                class="w-full h-full object-cover"
              />
            </div>
            <!-- Placeholder image if no hero image -->
            <div
              v-else
              class="aspect-video rounded-md overflow-hidden shadow-md ring-2 mb-6"
              :style="{ ringColor: COLORS.secondary }"
            >
              <img
                src="https://www.placeholderimage.online/placeholder/800/450/ededed/e6e6e6?text=Topic&font=Poppins.webp"
                alt="Topic Image"
                class="w-full h-full object-cover"
              />
            </div>

            <!-- Topic Description -->
            <div class="mb-6">
              <h2 class="text-xl font-semibold text-gray-900 mb-3">
                Mô tả bài học
              </h2>
              <p
                v-if="topicDetail[topicName]?.description"
                class="text-gray-600 leading-relaxed"
              >
                {{ topicDetail[topicName].description }}
              </p>
              <p v-else class="text-gray-500 italic">
                Không có mô tả cho bài học này
              </p>
            </div>
          </div>
        </div>
      </div>
      <div class="col-span-3 overflow-hidden rounded-lg shadow-xl bg-white">
        <!-- Homework Section -->
        <HomeworkSection
          :customHomework="topicDetail[topicName]?.custom_homework"
        />
      </div>
    </div>

    <!-- Loading state -->
    <div v-else class="flex items-center justify-center py-12">
      <div class="text-gray-500">Đang tải thông tin bài học...</div>
    </div>
  </div>
</template>
