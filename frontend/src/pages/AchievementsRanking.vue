<template>
  <section
    class="p-5 space-y-6 bg-gradient-to-br from-[#F25A23]/5 via-white to-[#F25A23]/5"
  >
    <div class="max-w-[760px] mx-auto">
      <div class="flex flex-col gap-4">
        <div>
          <h2 class="text-[25px] font-semibold uppercase text-primary">
            Leaderboard
          </h2>
          <p class="mt-1 text-sm text-slate-600">
            Chọn lớp để xem bảng xếp hạng tổng điểm huy hiệu của học sinh trong
            từng nhóm.
          </p>
        </div>
        <div class="flex flex-col gap-2 items-start">
          <p class="font-semibold text-primary uppercase">Lớp học sinh</p>
          <div class="relative w-86" @click.stop>
            <!-- Glow layer -->
            <div
              class="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-r from-[#F25A23]/15 via-white to-[#F25A23]/10 opacity-80"
            />
            <!-- Left icon -->
            <div
              class="pointer-events-none absolute inset-y-0 left-3 flex items-center"
            >
              <span
                class="inline-flex h-6 w-6 items-center justify-center rounded-full bg-[#F25A23]/10 text-sm shadow-sm z-10"
              >
                🏅
              </span>
            </div>
            <!-- Custom dropdown trigger -->
            <button
              type="button"
              class="relative flex w-full items-center justify-between rounded-2xl border border-gray-200 bg-white pl-11 pr-2.5 py-2.5 text-sm text-slate-800 shadow-xs focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-orange-500 hover:border-orange-500 transition-colors duration-200 text-left backdrop-blur-sm"
              @click="toggleDropdown"
              @keydown.escape.stop.prevent="closeDropdown"
            >
              <span v-if="selectedGroupOption" class="block">
                {{ selectedGroupOption.student_group_name }} —
                {{ selectedGroupOption.course }}
              </span>
              <span v-else class="block text-slate-400"> Chọn nhóm... </span>
              <span class="ml-2 flex items-center text-primary">
                <svg
                  class="h-4 w-4 transition-transform duration-150"
                  :class="{ 'rotate-180': isDropdownOpen }"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fill-rule="evenodd"
                    d="M5.23 7.21a.75.75 0 0 1 1.06.02L10 10.94l3.71-3.71a.75.75 0 1 1 1.06 1.06l-4.24 4.25a.75.75 0 0 1-1.06 0L5.21 8.27a.75.75 0 0 1 .02-1.06Z"
                    clip-rule="evenodd"
                  />
                </svg>
              </span>
            </button>
            <!-- Beautiful options panel -->
            <div
              v-if="isDropdownOpen"
              class="absolute z-20 mt-1 w-full rounded-2xl border border-[#F25A23]/20 bg-white shadow-2xl max-h-72 overflow-auto py-1 backdrop-blur-sm"
            >
              <button
                v-for="group in groups"
                :key="group.name"
                type="button"
                class="flex w-full items-center justify-between gap-2 px-3 py-2 text-sm text-left"
                :class="[
                  group.name === selectedGroupName
                    ? 'bg-[#F25A23]/10 text-primary font-semibold'
                    : 'text-slate-700',
                  'hover:bg-[#F25A23]/15 hover:text-primary transition-colors duration-150',
                ]"
                @click.stop="selectGroup(group)"
              >
                <span>
                  {{ group.student_group_name }} — {{ group.course }}
                </span>
                <span
                  v-if="group.name === selectedGroupName"
                  class="ml-2 text-[10px] uppercase tracking-[0.16em] text-primary"
                >
                  <Check />
                </span>
              </button>
              <div
                v-if="!groups.length"
                class="px-3 py-2 text-xs text-slate-400"
              >
                Chưa có nhóm nào
              </div>
            </div>
          </div>
        </div>
      </div>
      <div
        class="relative overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm mt-5"
      >
        <div class="relative p-5 sm:p-6 space-y-4">
          <div class="flex items-center justify-between gap-3 max-md:flex-col">
            <h3 class="text-base text-slate-800 uppercase font-semibold grow">
              {{ currentGroupLabel }}
            </h3>
            <p v-if="selectedStudents.length" class="text-xs shrink-0">
              Tổng số học sinh:
              <span class="font-semibold text-[#F25A23]">{{
                selectedStudents.length
              }}</span>
            </p>
          </div>
          <div v-if="loading" class="py-10 flex items-center justify-center">
            <p class="text-sm text-slate-600">
              Đang tải dữ liệu bảng xếp hạng...
            </p>
          </div>
          <div
            v-else-if="!groups.length"
            class="py-10 flex items-center justify-center"
          >
            <p class="text-sm text-slate-600">
              Chưa tìm thấy nhóm học sinh nào cho tài khoản này.
            </p>
          </div>
          <div
            v-else-if="!selectedStudents.length"
            class="py-10 flex items-center justify-center"
          >
            <p class="text-sm text-slate-600">
              Nhóm này chưa có học sinh nào hoặc chưa có điểm huy hiệu.
            </p>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="(student, index) in selectedStudents"
              :key="student.name"
              :class="[
                'relative flex items-center gap-2 md:gap-4 rounded-lg border px-5 py-4 transition-all duration-200 cursor-pointer',
                isCurrentStudent(student)
                  ? 'border-[#F25A23] bg-[#F25A23]/10 shadow-md ring-2 ring-[#F25A23]/20'
                  : 'border-gray-200 bg-white hover:border-[#F25A23]/40 hover:bg-[#F25A23]/5',
              ]"
              @click="openBadgeModal(student)"
            >
              <!-- Rank / Medal -->
              <div
                class="flex justify-center max-md:absolute max-md:top-0 max-md:left-0 max-md:-translate-y-1/2 max-md:-translate-x-1/2"
              >
                <!-- Top 1 -->
                <svg
                  v-if="index === 0"
                  class="size-6 md:size-8"
                  width="450"
                  height="448"
                  viewBox="0 0 450 448"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M449.062 353.41L363.697 354.977L347.095 439.976L212 278.977L314.462 193.001L449.062 353.41Z"
                    fill="#3F82C6"
                  />
                  <path
                    d="M0.479647 363.929L83.3692 365.452L99.4903 447.986L230.668 291.654L131.176 208.171L0.479647 363.929Z"
                    fill="#3F82C6"
                  />
                  <path
                    d="M196.946 24.0773C210.227 10.7837 231.773 10.7836 245.054 24.0773L258.067 37.1034C265.178 44.2217 275.077 47.8247 285.1 46.9428L303.442 45.329C322.16 43.682 338.666 57.5314 340.294 76.2516L341.89 94.5948C342.762 104.619 348.029 113.742 356.274 119.509L371.362 130.063C386.76 140.833 390.501 162.052 379.716 177.439L369.147 192.516C363.372 200.756 361.542 211.13 364.151 220.848L368.926 238.63C373.798 256.778 363.025 275.438 344.872 280.292L327.085 285.049C317.364 287.648 309.295 294.42 305.047 303.541L297.274 320.232C289.341 337.266 269.094 344.636 252.068 336.686L235.384 328.896C226.267 324.639 215.733 324.639 206.616 328.896L189.932 336.686C172.906 344.636 152.659 337.266 144.726 320.232L136.953 303.541C132.705 294.42 124.636 287.648 114.915 285.049L97.1278 280.292C78.9748 275.438 68.2018 256.779 73.0742 238.63L77.8485 220.848C80.4575 211.13 78.6283 200.756 72.8529 192.516L62.2845 177.439C51.4989 162.052 55.2403 140.833 70.6382 130.063L85.726 119.509C93.9711 113.742 99.2383 104.619 100.11 94.5948L101.706 76.2516C103.334 57.5315 119.84 43.682 138.558 45.329L156.9 46.9428C166.923 47.8247 176.822 44.2217 183.933 37.1034L196.946 24.0773Z"
                    fill="#FFCC20"
                  />
                  <circle cx="220.5" cy="181.5" r="115.5" fill="#FAA62A" />
                  <path
                    d="M195.047 197.801V145.652C195.047 143.569 194.331 142.039 192.898 141.062C191.531 140.086 189.839 139.5 187.82 139.305C185.867 139.044 183.882 138.816 181.863 138.621C179.91 138.361 178.217 137.677 176.785 136.57C175.418 135.398 174.734 133.641 174.734 131.297C174.734 127.195 175.613 122.215 177.371 116.355C179.194 110.431 181.18 106.753 183.328 105.32C196.674 106.167 207.482 106.59 215.75 106.59C220.958 106.59 226.525 106.199 232.449 105.418C238.439 104.572 242.117 104.083 243.484 103.953C247.977 103.953 250.223 106.362 250.223 111.18V195.848C250.223 199.428 250.288 202.488 250.418 205.027C250.613 207.501 250.939 210.268 251.395 213.328C251.915 216.323 252.762 218.699 253.934 220.457C255.105 222.15 256.603 223.094 258.426 223.289C259.598 223.484 260.477 223.68 261.062 223.875C261.714 224.005 262.462 224.298 263.309 224.754C264.22 225.21 264.871 225.861 265.262 226.707C265.652 227.553 265.848 228.595 265.848 229.832C265.848 234.715 265.164 239.76 263.797 244.969C262.495 250.177 260.639 253.4 258.23 254.637C248.79 252.879 238.406 252 227.078 252C211.844 252 198.53 252.879 187.137 254.637C184.728 253.4 182.84 250.177 181.473 244.969C180.171 239.76 179.52 234.715 179.52 229.832C179.52 228.595 179.715 227.553 180.105 226.707C180.496 225.861 181.115 225.21 181.961 224.754C182.872 224.298 183.621 224.005 184.207 223.875C184.858 223.68 185.77 223.484 186.941 223.289C188.634 223.094 190.034 222.28 191.141 220.848C192.312 219.35 193.159 217.299 193.68 214.695C194.201 212.026 194.559 209.422 194.754 206.883C194.949 204.344 195.047 201.316 195.047 197.801Z"
                    fill="white"
                  />
                </svg>
                <!-- Top 2 -->
                <svg
                  v-else-if="index === 1"
                  class="size-6 md:size-8"
                  width="450"
                  height="448"
                  viewBox="0 0 450 448"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M449.062 353.41L363.697 354.977L347.095 439.976L212 278.977L314.462 193.001L449.062 353.41Z"
                    fill="#3F82C6"
                  />
                  <path
                    d="M0.479647 363.929L83.3692 365.452L99.4903 447.986L230.668 291.654L131.176 208.171L0.479647 363.929Z"
                    fill="#3F82C6"
                  />
                  <path
                    d="M196.946 24.0773C210.227 10.7837 231.773 10.7836 245.054 24.0773L258.067 37.1034C265.178 44.2217 275.077 47.8247 285.1 46.9428L303.442 45.329C322.16 43.682 338.666 57.5314 340.294 76.2516L341.89 94.5948C342.762 104.619 348.029 113.742 356.274 119.509L371.362 130.063C386.76 140.833 390.501 162.052 379.716 177.439L369.147 192.516C363.372 200.756 361.542 211.13 364.151 220.848L368.926 238.63C373.798 256.778 363.025 275.438 344.872 280.292L327.085 285.049C317.364 287.648 309.295 294.42 305.047 303.541L297.274 320.232C289.341 337.266 269.094 344.636 252.068 336.686L235.384 328.896C226.267 324.639 215.733 324.639 206.616 328.896L189.932 336.686C172.906 344.636 152.659 337.266 144.726 320.232L136.953 303.541C132.705 294.42 124.636 287.648 114.915 285.049L97.1278 280.292C78.9748 275.438 68.2018 256.779 73.0742 238.63L77.8485 220.848C80.4575 211.13 78.6283 200.756 72.8529 192.516L62.2845 177.439C51.4989 162.052 55.2403 140.833 70.6382 130.063L85.726 119.509C93.9711 113.742 99.2383 104.619 100.11 94.5948L101.706 76.2516C103.334 57.5315 119.84 43.682 138.558 45.329L156.9 46.9428C166.923 47.8247 176.822 44.2217 183.933 37.1034L196.946 24.0773Z"
                    fill="#B9B9BC"
                  />
                  <circle cx="220.5" cy="181.5" r="115.5" fill="#3E414A" />
                  <path
                    d="M169.676 109.812C175.926 108.12 184.52 106.753 195.457 105.711C206.46 104.669 218.081 104.148 230.32 104.148C236.049 104.148 241.583 104.507 246.922 105.223C252.326 105.874 257.632 107.046 262.84 108.738C268.048 110.366 272.573 112.417 276.414 114.891C280.255 117.365 283.348 120.587 285.691 124.559C288.1 128.465 289.305 132.859 289.305 137.742C289.305 143.471 288.263 149.07 286.18 154.539C284.096 160.008 281.525 164.826 278.465 168.992C275.47 173.094 271.661 177.391 267.039 181.883C262.417 186.375 258.152 190.151 254.246 193.211C250.34 196.206 245.815 199.721 240.672 203.758C235.529 207.729 231.557 210.952 228.758 213.426H233.445C235.984 213.426 238.133 213.393 239.891 213.328C241.714 213.198 244.188 212.807 247.312 212.156C250.438 211.505 253.139 210.626 255.418 209.52C257.762 208.348 260.138 206.59 262.547 204.246C265.021 201.902 267.007 199.103 268.504 195.848C273.582 193.634 277.944 192.527 281.59 192.527C282.632 192.527 283.836 192.69 285.203 193.016C286.635 193.341 288.1 193.829 289.598 194.48C291.095 195.132 292.365 196.108 293.406 197.41C294.448 198.712 294.969 200.21 294.969 201.902C294.969 206.655 293.146 214.077 289.5 224.168C285.854 234.194 282.762 241.551 280.223 246.238C274.754 250.21 249.266 252.195 203.758 252.195C198.419 252.195 191.616 252.163 183.348 252.098C175.145 252.033 169.871 252 167.527 252C165.314 251.219 163.035 249.07 160.691 245.555C158.348 241.974 157.046 238.491 156.785 235.105C156.85 234.129 157.241 232.892 157.957 231.395C158.738 229.897 159.943 228.107 161.57 226.023C163.198 223.875 164.728 221.922 166.16 220.164C167.658 218.341 169.708 216.03 172.312 213.23C174.917 210.366 177 208.087 178.562 206.395C180.125 204.637 182.371 202.228 185.301 199.168C188.296 196.043 190.379 193.862 191.551 192.625C200.47 183.185 207.957 173.745 214.012 164.305C220.066 154.865 223.094 146.499 223.094 139.207C223.094 130.353 220.294 125.926 214.695 125.926C211.701 125.926 207.99 127.326 203.562 130.125C199.135 132.924 195.034 136.147 191.258 139.793C187.547 143.374 184.324 146.629 181.59 149.559C178.855 152.488 177.326 154.279 177 154.93C173.094 154.93 168.536 153.855 163.328 151.707C158.185 149.559 155.613 147.345 155.613 145.066C155.613 137.319 157.078 130.092 160.008 123.387C162.938 116.681 166.16 112.156 169.676 109.812Z"
                    fill="#E5E5E5"
                  />
                </svg>
                <!-- Top 3 -->
                <svg
                  v-else-if="index === 2"
                  class="size-6 md:size-8"
                  width="450"
                  height="448"
                  viewBox="0 0 450 448"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M449.062 353.41L363.697 354.977L347.095 439.976L212 278.977L314.462 193.001L449.062 353.41Z"
                    fill="#3F82C6"
                  />
                  <path
                    d="M0.479647 363.929L83.3692 365.452L99.4903 447.986L230.668 291.654L131.176 208.171L0.479647 363.929Z"
                    fill="#3F82C6"
                  />
                  <path
                    d="M196.946 24.0773C210.227 10.7837 231.773 10.7836 245.054 24.0773L258.067 37.1034C265.178 44.2217 275.077 47.8247 285.1 46.9428L303.442 45.329C322.16 43.682 338.666 57.5314 340.294 76.2516L341.89 94.5948C342.762 104.619 348.029 113.742 356.274 119.509L371.362 130.063C386.76 140.833 390.501 162.052 379.716 177.439L369.147 192.516C363.372 200.756 361.542 211.13 364.151 220.848L368.926 238.63C373.798 256.778 363.025 275.438 344.872 280.292L327.085 285.049C317.364 287.648 309.295 294.42 305.047 303.541L297.274 320.232C289.341 337.266 269.094 344.636 252.068 336.686L235.384 328.896C226.267 324.639 215.733 324.639 206.616 328.896L189.932 336.686C172.906 344.636 152.659 337.266 144.726 320.232L136.953 303.541C132.705 294.42 124.636 287.648 114.915 285.049L97.1278 280.292C78.9748 275.438 68.2018 256.779 73.0742 238.63L77.8485 220.848C80.4575 211.13 78.6283 200.756 72.8529 192.516L62.2845 177.439C51.4989 162.052 55.2403 140.833 70.6382 130.063L85.726 119.509C93.9711 113.742 99.2383 104.619 100.11 94.5948L101.706 76.2516C103.334 57.5315 119.84 43.682 138.558 45.329L156.9 46.9428C166.923 47.8247 176.822 44.2217 183.933 37.1034L196.946 24.0773Z"
                    fill="#D89562"
                  />
                  <circle cx="220.5" cy="181.5" r="115.5" fill="#894630" />
                  <path
                    d="M170.586 250.828C165.964 248.549 161.276 244.415 156.523 238.426C151.771 232.436 149.395 227.065 149.395 222.312C149.395 218.797 151.673 215.379 156.23 212.059C160.853 208.738 165.215 207.078 169.316 207.078C169.707 207.078 170.846 207.827 172.734 209.324C174.688 210.822 176.934 212.449 179.473 214.207C182.012 215.965 185.658 217.592 190.41 219.09C195.228 220.587 200.339 221.336 205.742 221.336C222.539 221.336 230.938 215.379 230.938 203.465C230.938 198.257 229.277 193.895 225.957 190.379C222.637 186.798 218.73 184.845 214.238 184.52C210.332 184.259 207.305 184.129 205.156 184.129C202.943 184.129 199.85 184.227 195.879 184.422C191.908 184.617 189.271 184.715 187.969 184.715C186.471 184.585 185.332 183.608 184.551 181.785C183.835 179.897 183.477 176.609 183.477 171.922C183.477 165.086 185.267 160.854 188.848 159.227C190.736 159.422 192.591 159.52 194.414 159.52C205.417 159.454 213.457 157.892 218.535 154.832C223.613 151.707 226.152 147.54 226.152 142.332C226.152 137.84 224.753 134.096 221.953 131.102C219.154 128.042 215.768 126.512 211.797 126.512C207.826 126.512 204.115 127.391 200.664 129.148C197.214 130.906 194.349 133.055 192.07 135.594C189.792 138.068 187.708 140.542 185.82 143.016C183.997 145.49 182.305 147.605 180.742 149.363C179.18 151.121 177.78 152 176.543 152C170.814 152 165.801 150.828 161.504 148.484C157.272 146.141 155.156 144.025 155.156 142.137C155.156 132.827 157.826 124.526 163.164 117.234C168.503 109.878 174.362 105.874 180.742 105.223C188.359 104.507 203.138 104.148 225.078 104.148C232.109 104.148 238.457 104.767 244.121 106.004C249.785 107.176 254.505 108.803 258.281 110.887C262.057 112.97 265.215 115.411 267.754 118.211C270.293 121.01 272.116 123.94 273.223 127C274.329 130.06 274.883 133.283 274.883 136.668C274.883 142.853 272.865 148.615 268.828 153.953C264.857 159.292 259.714 162.84 253.398 164.598C260.495 165.184 267.07 167.527 273.125 171.629C279.18 175.73 283.867 180.678 287.188 186.473C290.573 192.202 292.266 197.964 292.266 203.758C292.266 212.156 290.345 219.643 286.504 226.219C282.728 232.794 277.487 238.133 270.781 242.234C264.141 246.271 256.458 249.363 247.734 251.512C239.076 253.595 229.668 254.637 219.512 254.637C204.538 254.637 188.229 253.367 170.586 250.828Z"
                    fill="white"
                  />
                </svg>
                <!-- Other ranks -->
                <div
                  v-else
                  class="inline-flex size-6 md:size-8 items-center justify-center rounded-full border border-primary md:border-slate-300 bg-white text-xs font-semibold text-primary md:text-slate-500"
                >
                  {{ index + 1 }}
                </div>
              </div>
              <!-- Avatar: ưu tiên ảnh, fallback chữ cái đầu -->
              <div
                class="flex size-10 flex-shrink-0 items-center justify-center rounded-full bg-primary text-white text-sm font-semibold overflow-hidden border-primary"
              >
                <img
                  v-if="student.image"
                  :src="student.image"
                  :alt="student.student_name || 'Student avatar'"
                  class="h-full w-full object-cover"
                />
                <span v-else>
                  {{ student.student_name?.trim()?.charAt(0) || '?' }}
                </span>
              </div>
              <!-- Name + stars -->
              <div class="min-w-0 flex items-center justify-between gap-4 grow">
                <div
                  class="min-w-0 flex md:items-center gap-2 md:gap-3 w-full justify-between max-md:flex-col md:pr-3"
                >
                  <div class="flex items-center gap-2">
                    <p
                      class="text-base font-semibold"
                      :class="
                        isCurrentStudent(student)
                          ? 'text-[#F25A23]'
                          : 'text-slate-900'
                      "
                    >
                      {{ student.student_name || 'Không rõ tên' }}
                    </p>
                    <!-- <span v-if="isCurrentStudent(student)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-[#F25A23] text-white">
                      
                    </span> -->
                  </div>
                  <div class="flex items-center gap-1 md:gap-1.5">
                    <Star
                      v-for="star in 5"
                      :key="star"
                      class="size-5"
                      :class="
                        star <= starCount(student)
                          ? 'text-[#F25A23] fill-[#F25A23]'
                          : 'text-slate-300'
                      "
                    />
                  </div>
                </div>
              </div>
              <!-- Points -->
              <div class="flex flex-col items-center gap-0.5 text-center">
                <span class="text-lg font-bold text-primary tabular-nums">
                  {{ toNumber(student.group_badge_points) }}
                </span>
                <span class="text-[11px] uppercase tracking-[0.18em]">
                  Điểm
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Badge Modal -->
  <div
    v-if="isBadgeModalOpen && selectedStudent"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
    role="dialog"
    aria-modal="true"
    @click.self="closeBadgeModal"
  >
    <div
      class="w-full max-w-[600px] rounded-lg md:rounded-2xl bg-white shadow-2xl overflow-hidden"
    >
      <div class="w-full max-h-[94svh] overflow-y-auto">
        <!-- Loading state -->
        <div
          v-if="loadingBadges"
          class="py-20 flex items-center justify-center"
        >
          <p class="text-sm text-slate-600">Đang tải huy hiệu...</p>
        </div>

        <!-- No badges -->
        <div v-else-if="!studentBadges.length" class="relative">
          <!-- Header with student info -->
          <div
            class="relative bg-gradient-to-br from-orange-300 via-orange-400 to-orange-500 p-6"
          >
            <div class="flex items-center gap-4">
              <div
                class="flex size-16 flex-shrink-0 items-center justify-center rounded-full bg-white text-primary text-xl font-bold overflow-hidden border-2 border-white shadow-lg"
              >
                <img
                  v-if="selectedStudent.image"
                  :src="selectedStudent.image"
                  :alt="selectedStudent.student_name"
                  class="h-full w-full object-cover"
                />
                <span v-else>
                  {{ selectedStudent.student_name?.trim()?.charAt(0) || '?' }}
                </span>
              </div>
              <div class="text-white">
                <h3 class="text-xl font-bold">
                  {{ selectedStudent.student_name || 'Học sinh' }}
                </h3>
                <p class="text-sm text-white/80">
                  {{ toNumber(selectedStudent.group_badge_points) }} điểm huy
                  hiệu
                </p>
              </div>
            </div>
            <button
              type="button"
              class="absolute right-3 top-3 h-9 w-9 rounded-full bg-white/80 text-gray-700 transition-all duration-300 hover:bg-white shadow flex items-center justify-center text-base font-semibold"
              @click="closeBadgeModal"
              aria-label="Đóng"
            >
              &times;
            </button>
          </div>
          <div
            class="py-10 flex flex-col items-center justify-center text-center p-6"
          >
            <div class="text-4xl mb-3">🏅</div>
            <p class="text-sm text-slate-600">
              Học sinh này chưa có huy hiệu nào trong lớp này.
            </p>
          </div>
        </div>

        <!-- Has badges - Show like Achievement.vue -->
        <template v-else>
          <!-- Badge image header -->
          <div
            class="relative h-[300px] max-h-[62vw] bg-gradient-to-br from-orange-300 via-orange-400 to-orange-500 flex items-center justify-center"
          >
            <figure class="h-full aspect-square">
              <img
                :src="getBadgeImage(currentBadge)"
                :alt="currentBadge.badge_name"
                class="h-full w-full object-cover drop-shadow-xl transition-all duration-300"
              />
            </figure>
            <button
              type="button"
              class="absolute right-3 top-3 h-9 w-9 rounded-full bg-white/80 text-gray-700 transition-all duration-300 hover:bg-white shadow flex items-center justify-center text-base font-semibold"
              @click="closeBadgeModal"
              aria-label="Đóng"
            >
              &times;
            </button>
            <!-- Navigation arrows for multiple badges -->
            <template v-if="studentBadges.length > 1">
              <button
                type="button"
                class="absolute left-3 top-1/2 -translate-y-1/2 h-10 w-10 rounded-full bg-white/80 shadow-lg flex items-center justify-center text-gray-600 hover:bg-white transition-colors"
                @click="prevBadge"
              >
                <ChevronLeft class="w-5 h-5" />
              </button>
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 h-10 w-10 rounded-full bg-white/80 shadow-lg flex items-center justify-center text-gray-600 hover:bg-white transition-colors"
                @click="manualNextBadge"
              >
                <ChevronRight class="w-5 h-5" />
              </button>
            </template>
          </div>

          <!-- Badge content -->
          <div class="p-6 space-y-4">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <h4 class="text-xl font-semibold text-gray-900">
                  {{ currentBadge.badge_name || 'Huy hiệu' }}
                </h4>
                <span
                  v-if="currentBadge.student_group"
                  class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                  style="
                    background-color: #fef3c7;
                    color: #92400e;
                    border: 1px solid #fcd34d;
                  "
                >
                  {{ currentBadge.student_group }}
                </span>
              </div>
              <p
                v-if="currentBadge.badge_description"
                class="mt-2 text-sm text-gray-600 leading-snug"
                v-html="currentBadge.badge_description"
              ></p>
              <div class="mt-3 flex items-center gap-3 text-sm text-gray-700">
                <span
                  class="flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1"
                >
                  <span class="text-orange-500">◆</span> Level
                  {{ currentBadge.badge_level || 'N/A' }}
                </span>
                <span
                  class="flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1"
                >
                  <span class="text-amber-500">★</span>
                  {{ toNumber(currentBadge.badge_points) }} điểm
                </span>
              </div>
            </div>

            <!-- Progress message -->
            <div
              class="rounded-xl bg-emerald-50 border border-emerald-200 px-4 py-3"
            >
              <p class="text-sm leading-snug text-green-600 font-semibold">
                🎉 Chúc mừng đã đạt được huy hiệu này! Cảm ơn bạn đã đóng góp
                tích cực và giúp cộng đồng phát triển tốt hơn mỗi ngày.
              </p>
            </div>

            <!-- Criteria section -->
            <div
              v-if="currentBadge.badge_criteria"
              class="rounded-xl border border-gray-200"
            >
              <div class="border-b border-gray-200 px-4 py-3">
                <p class="font-semibold text-gray-900 flex items-center gap-2">
                  <span class="size-5 text-green-500">
                    <svg
                      width="100%"
                      height="100%"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M16.19 2H7.81C4.17 2 2 4.17 2 7.81V16.18C2 19.83 4.17 22 7.81 22H16.18C19.82 22 21.99 19.83 21.99 16.19V7.81C22 4.17 19.83 2 16.19 2ZM16.78 9.7L11.11 15.37C10.97 15.51 10.78 15.59 10.58 15.59C10.38 15.59 10.19 15.51 10.05 15.37L7.22 12.54C6.93 12.25 6.93 11.77 7.22 11.48C7.51 11.19 7.99 11.19 8.28 11.48L10.58 13.78L15.72 8.64C16.01 8.35 16.49 8.35 16.78 8.64C17.07 8.93 17.07 9.4 16.78 9.7Z"
                        fill="currentColor"
                      />
                    </svg>
                  </span>
                  <span>Tiêu chí để đạt được huy hiệu</span>
                </p>
              </div>
              <div class="px-4 py-3 space-y-3">
                <div
                  class="achievement-criteria text-sm text-gray-700 leading-relaxed"
                  v-html="currentBadge.badge_criteria"
                ></div>
              </div>
            </div>

            <!-- Dots indicator for multiple badges -->
            <div
              v-if="studentBadges.length > 1"
              class="flex items-center justify-center gap-2 pt-2"
            >
              <button
                v-for="(badge, idx) in studentBadges"
                :key="badge.name"
                type="button"
                class="h-2 rounded-full transition-all duration-200"
                :class="
                  idx === currentBadgeIndex
                    ? 'w-6 bg-primary'
                    : 'w-2 bg-gray-300 hover:bg-gray-400'
                "
                @click="goToBadge(idx)"
              />
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
<script setup>
import { studentStore } from '@/stores/student'
import { createResource } from 'frappe-ui'
import { Check, ChevronLeft, ChevronRight, Star } from 'lucide-vue-next'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const { studentInfo } = studentStore()

const groups = ref([])
const selectedGroupName = ref('')
const loading = ref(false)
const isDropdownOpen = ref(false)

// Badge modal state
const isBadgeModalOpen = ref(false)
const selectedStudent = ref(null)
const studentBadges = ref([])
const loadingBadges = ref(false)
const currentBadgeIndex = ref(0)
let autoSlideInterval = null

const allStudentGroups = createResource({
  url: 'education.education.api.get_all_student_groups_with_badge_points',
  auto: false,
})

const studentBadgesResource = createResource({
  url: 'education.education.api.get_student_badges_in_group',
  auto: false,
})

onMounted(async () => {
  const studentName = studentInfo?.name || studentInfo?.value?.name
  if (!studentName) {
    console.warn('Không tìm thấy student name để gọi get_all_student_groups')
    return
  }

  try {
    loading.value = true
    const data = await allStudentGroups.reload({ student: studentName })
    groups.value = Array.isArray(data) ? data : []

    if (groups.value.length > 0) {
      selectedGroupName.value = groups.value[0].name
    }

    console.log('All student groups for student', studentName, ':', data)
  } catch (error) {
    console.error('Failed to load all student groups', error)
  } finally {
    loading.value = false
  }

  window.addEventListener('click', handleClickOutside)
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', handleClickOutside)
  window.removeEventListener('keydown', handleKeydown)
  stopAutoSlide()
})

const toNumber = (value) => {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

const selectedGroup = computed(() =>
  groups.value.find((g) => g.name === selectedGroupName.value),
)

const selectedGroupOption = computed(() => selectedGroup.value || null)

const selectedStudents = computed(() => {
  if (!selectedGroup.value || !Array.isArray(selectedGroup.value.students))
    return []
  return [...selectedGroup.value.students].sort(
    (a, b) => toNumber(b.group_badge_points) - toNumber(a.group_badge_points),
  )
})

const currentGroupLabel = computed(() => {
  if (!selectedGroup.value) return 'Chưa chọn nhóm'
  return `${selectedGroup.value.student_group_name} • ${selectedGroup.value.course}`
})

const toggleDropdown = () => {
  if (!groups.value.length) return
  isDropdownOpen.value = !isDropdownOpen.value
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}

const handleClickOutside = (event) => {
  // dropdown wrapper có @click.stop, nên chỉ cần close khi click ngoài window
  if (isDropdownOpen.value) {
    isDropdownOpen.value = false
  }
}

const starCount = (student) => {
  const points = toNumber(student.group_badge_points)
  if (points >= 400) return 5
  if (points >= 250) return 4
  if (points >= 150) return 3
  if (points >= 50) return 2
  if (points > 0) return 1
  return 0
}

const isCurrentStudent = (student) => {
  const currentStudentName = studentInfo?.name || studentInfo?.value?.name
  return student?.name === currentStudentName
}

const selectGroup = (group) => {
  selectedGroupName.value = group.name
  isDropdownOpen.value = false
}

// Badge modal functions
const currentBadge = computed(() => {
  if (!studentBadges.value.length) return null
  return studentBadges.value[currentBadgeIndex.value] || studentBadges.value[0]
})

const getBadgeImage = (badge) => {
  if (badge?.badge_link_image) {
    return 'https://education.windify.edu.vn' + badge.badge_link_image
  }
  return 'https://education.windify.edu.vn/files/robot-acedemy-52.png'
}

const openBadgeModal = async (student) => {
  selectedStudent.value = student
  currentBadgeIndex.value = 0
  studentBadges.value = []
  isBadgeModalOpen.value = true
  loadingBadges.value = true

  try {
    const data = await studentBadgesResource.reload({
      student: student.name,
      student_group: selectedGroupName.value,
    })
    studentBadges.value = Array.isArray(data) ? data : []
    // Start auto-slide if multiple badges
    startAutoSlide()
  } catch (error) {
    console.error('Failed to load student badges', error)
    studentBadges.value = []
  } finally {
    loadingBadges.value = false
  }
}

const closeBadgeModal = () => {
  stopAutoSlide()
  isBadgeModalOpen.value = false
  selectedStudent.value = null
  studentBadges.value = []
  currentBadgeIndex.value = 0
}

const startAutoSlide = () => {
  stopAutoSlide()
  if (studentBadges.value.length > 1) {
    autoSlideInterval = setInterval(() => {
      nextBadge()
    }, 2000) // 4 seconds
  }
}

const stopAutoSlide = () => {
  if (autoSlideInterval) {
    clearInterval(autoSlideInterval)
    autoSlideInterval = null
  }
}

const resetAutoSlide = () => {
  // Reset timer when user manually navigates
  if (studentBadges.value.length > 1) {
    startAutoSlide()
  }
}

const prevBadge = () => {
  if (currentBadgeIndex.value > 0) {
    currentBadgeIndex.value--
  } else {
    currentBadgeIndex.value = studentBadges.value.length - 1
  }
  resetAutoSlide()
}

const nextBadge = () => {
  if (currentBadgeIndex.value < studentBadges.value.length - 1) {
    currentBadgeIndex.value++
  } else {
    currentBadgeIndex.value = 0
  }
}

const manualNextBadge = () => {
  nextBadge()
  resetAutoSlide()
}

const goToBadge = (idx) => {
  currentBadgeIndex.value = idx
  resetAutoSlide()
}

// Handle keyboard navigation
const handleKeydown = (event) => {
  if (!isBadgeModalOpen.value) return
  if (event.key === 'Escape') {
    closeBadgeModal()
  } else if (event.key === 'ArrowLeft') {
    prevBadge()
  } else if (event.key === 'ArrowRight') {
    if (currentBadgeIndex.value < studentBadges.value.length - 1) {
      currentBadgeIndex.value++
    } else {
      currentBadgeIndex.value = 0
    }
    resetAutoSlide()
  }
}
</script>

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
