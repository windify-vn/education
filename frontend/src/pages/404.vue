<script setup>
import { useRouter } from 'vue-router'
import { GraduationCap, BookOpen, MonitorPlay, Shield } from 'lucide-vue-next'
import { COLORS, GRADIENTS } from '@/constants/colors'

const router = useRouter()

function goHome() {
  router.push('/profile')
}

function goPrograms() {
  router.push('/program')
}
</script>

<template>
  <div class="min-h-[80vh] w-full flex items-center justify-center p-6 overflow-hidden bg-gradient-to-br from-[#FFF7F3] via-white to-[#FFF0EA] relative">
    <!-- Animated Background Orbs -->
    <div class="absolute -top-20 -left-20 w-72 h-72 rounded-full blur-3xl opacity-40"
         :style="{ background: `radial-gradient(circle at 30% 30%, ${COLORS.primary} 0%, transparent 60%)` }"></div>
    <div class="absolute -bottom-24 -right-24 w-80 h-80 rounded-full blur-3xl opacity-40"
         :style="{ background: `radial-gradient(circle at 70% 70%, ${COLORS.primaryLight} 0%, transparent 60%)` }"></div>

    <!-- Content -->
    <div class="relative z-10 w-full max-w-5xl bg-white/70 backdrop-blur-md rounded-2xl shadow-2xl border border-white/60">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-0">
        <!-- Illustration -->
        <div class="relative p-8 lg:p-12 flex items-center justify-center">
          <div class="relative w-full max-w-md">
            <!-- Big 404 -->
            <div class="text-center select-none">
              <span class="block text-[85px] md:text-[110px] font-black leading-none gradient-text drop-shadow-sm">404</span>
              <p class="mt-2 text-sm md:text-base text-gray-500">Trang bạn tìm kiếm không tồn tại</p>
            </div>

            <!-- Floating academic items (Lucide icons) -->
            <div class="absolute inset-0 pointer-events-none">
              <GraduationCap :style="{ color: COLORS.primary }" class="floating-1 absolute -top-4 -left-6 w-12 h-12" />
              <BookOpen :style="{ color: COLORS.primaryLight }" class="floating-2 absolute top-6 -right-4 w-10 h-10" />
              <MonitorPlay :style="{ color: COLORS.primary }" class="floating-3 absolute bottom-8 -left-2 w-10 h-10" />
              <Shield :style="{ color: COLORS.primaryLight }" class="floating-4 absolute -bottom-4 right-6 w-12 h-12" />
            </div>
          </div>
        </div>

        <!-- Copy & Actions -->
        <div class="p-8 lg:p-12 flex flex-col justify-center gap-6">
          <div>
            <h1 class="text-2xl md:text-3xl font-extrabold text-gray-900">Oops! Bạn đi lạc rồi ✨</h1>
            <p class="mt-3 text-sm md:text-base text-gray-600">Có vẻ bạn đã đi nhầm lớp. Hãy quay lại trang chính hoặc khám phá chương trình học dành cho bạn.</p>
          </div>

          <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <button @click="goHome" class="btn-primary">
              Về trang chính
            </button>
            <button @click="goPrograms" class="btn-secondary">
              Xem chương trình học
            </button>
          </div>

          <!-- Tips -->
          <div class="mt-2 text-xs md:text-sm text-gray-500">
            Mẹo: Kiểm tra lại đường dẫn, hoặc dùng menu để điều hướng nhanh hơn.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.gradient-text {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@keyframes float1 {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.95; }
  50% { transform: translateY(-10px) rotate(-4deg); opacity: 1; }
}
@keyframes float2 {
  0%, 100% { transform: translateY(0) rotate(0deg) scale(1); opacity: 0.9; }
  50% { transform: translateY(-8px) rotate(6deg) scale(1.03); opacity: 1; }
}
@keyframes float3 {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-12px) rotate(-8deg); }
}
@keyframes float4 {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-6px) rotate(8deg); }
}

.floating-1 { animation: float1 3.4s ease-in-out infinite; filter: drop-shadow(0 4px 10px rgba(242,90,35,0.25)); }
.floating-2 { animation: float2 4.1s ease-in-out infinite; filter: drop-shadow(0 4px 10px rgba(241,146,85,0.25)); }
.floating-3 { animation: float3 3.8s ease-in-out infinite; filter: drop-shadow(0 4px 10px rgba(242,90,35,0.2)); }
.floating-4 { animation: float4 4.6s ease-in-out infinite; filter: drop-shadow(0 4px 10px rgba(241,146,85,0.2)); }

.btn-primary {
  @apply inline-flex items-center justify-center px-5 py-3 rounded-lg font-semibold text-white shadow-md transition-all;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
}
.btn-primary:hover { filter: brightness(1.05); transform: translateY(-1px); }

.btn-secondary {
  @apply inline-flex items-center justify-center px-5 py-3 rounded-lg font-semibold border bg-white transition-all shadow-sm;
  color: var(--color-primary);
  border-color: var(--color-primary);
}
.btn-secondary:hover { background: #FFF5EF; transform: translateY(-1px); }
</style>

