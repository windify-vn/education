<script>
import ExternalLink from '@/components/icons/ExternalLink.vue'
import ArrowUpRight from '@/components/icons/ArrowUpRight.vue'
import { MoveUpRight } from 'lucide-vue-next'

export default {
  name: 'LearningPage',
  components: {
    ExternalLink,
    ArrowUpRight,
    MoveUpRight
  },
  data() {
    return {
      rcbUrl: 'https://windify.edu.vn'
    }
  },
  computed: {
    siteHost() {
      return window?.location?.origin || ''
    }
  },
  head() {
    return {
      title: 'Learning Workspace - Future Academy',
      meta: [
        {
          name: 'description',
          content: 'Chọn workspace học tập'
        }
      ]
    }
  }
}
</script>


<template>
  <div class="p-4 sm:p-6 md:p-8 lg:p-12 xl:p-[60px] min-h-screen">
    <div class="max-w-[1300px] mx-auto">
      <div
        class="flex justify-center items-center flex-col w-full mx-auto gap-6 sm:gap-8 lg:gap-10 mb-6 sm:mb-8 lg:mb-10">
        <div class="flex flex-col w-max relative px-4 sm:px-0">
          <div class="absolute top-0 left-0 -translate-x-[100%] -translate-y-1/2 hidden sm:block">
            <img :src="siteHost + '/files/abstract-line.png'" alt="" class="w-auto h-8 lg:h-12" />
          </div>
          <h1
            class="text-2xl sm:text-3xl md:text-4xl lg:text-[40px] font-semibold text-center sm:text-left leading-tight">
            Thắp Lửa Đam Mê lập trình
          </h1>
          <span class="text-sm sm:text-base md:text-lg lg:text-xl text-center sm:text-left mt-2 max-w-2xl">
            Tạo, chơi & học từ 200 video hướng dẫn và các dự án thực hành
          </span>
        </div>

        <div class="flex flex-col sm:flex-row gap-4 sm:gap-6 lg:gap-10 w-full text-white">
          <a href="https://robo.windify.edu.vn" target="_blank"
            class="relative flex-1 bg-gradient-to-t from-[var(--color-primary)] to-[var(--color-primary-light)] rounded-lg h-[100px] sm:h-[120px] hover:opacity-80 transition-opacity duration-300">
            <div
              class="flex justify-between items-start size-full text-lg sm:text-xl md:text-2xl lg:text-3xl font-semibold h-full py-3 sm:py-4 px-4 sm:px-5">
              <span class="leading-tight">Thực hiện<br class="sm:hidden"> lập trình</span>
              <div class="p-1.5 sm:p-2 bg-white rounded flex-shrink-0">
                <MoveUpRight class="text-[var(--color-primary)] w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6" />
              </div>
            </div>
            <div class="absolute bottom-1/2 left-3 sm:left-4 translate-y-1/2">
              <img :src="siteHost + '/files/code-vector.png'" alt=""
                class="opacity-20 max-h-[60px] sm:max-h-[80px] lg:max-h-[100px]">
            </div>
          </a>

          <a href="/learning/elearning" target="_blank"
            class="relative flex-1 bg-gradient-to-t from-[#224773] to-[#4086D9] rounded-lg h-[100px] sm:h-[120px] hover:opacity-80 transition-opacity duration-300">
            <div
              class="flex justify-between items-start size-full text-lg sm:text-xl md:text-2xl lg:text-3xl font-semibold h-full py-3 sm:py-4 px-4 sm:px-5">
              <span class="leading-tight">Tài liệu<br class="sm:hidden"> khoá học</span>
              <div class="p-1.5 sm:p-2 bg-white rounded flex-shrink-0">
                <MoveUpRight class="text-[#224773] w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6" />
              </div>
            </div>
            <div class="absolute bottom-1/2 left-3 sm:left-4 translate-y-1/2">
              <img :src="siteHost + '/files/doc-vector.png'" alt=""
                class="opacity-20 max-h-[60px] sm:max-h-[80px] lg:max-h-[100px]">
            </div>
          </a>
        </div>
      </div>

      <div
        class="flex flex-col lg:flex-row justify-center items-center w-full mx-auto gap-4 sm:gap-6 lg:gap-10 overflow-hidden">
        <img :src="siteHost + '/files/document-course.png'" alt=""
          class="w-full lg:w-1/2 h-auto object-contain max-h-[300px] sm:max-h-[400px] lg:max-h-none" />
        <img :src="siteHost + '/files/implement-code.png'" alt=""
          class="w-full lg:w-1/2 h-auto object-contain max-h-[300px] sm:max-h-[400px] lg:max-h-none" />
      </div>
    </div>
  </div>
</template>
