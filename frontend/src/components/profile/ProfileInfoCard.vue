<template>
  <div class="col-span-1 rounded-lg overflow-hidden border bg-white p-4 shadow-xl">
    <div class="font-semibold">Thông tin cá nhân</div>
    <div class="border-b border-gray-200 mt-2 mb-4"></div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="space-y-4 col-span-1">
        <InfoRow label="Student ID" :value="studentInfo?.name">
          <template #icon>
            <IdCard class="size-4 text-[var(--color-secondary)]" />
          </template>
        </InfoRow>
        <InfoRow label="Họ và tên" :value="studentInfo?.student_name">
          <template #icon>
            <User class="size-4 text-[var(--color-primary)]" />
          </template>
        </InfoRow>

        <InfoRow label="Email" :value="user?.data?.email">
          <template #icon>
            <Mail class="size-4 text-[var(--color-secondary)]" />
          </template>
        </InfoRow>
        <InfoRow label="Số điện thoại" :value="studentInfo?.student_mobile_number">
          <template #icon>
            <Phone class="size-4 text-[var(--color-primary)]" />
          </template>
        </InfoRow>
        <InfoRow label="Ngày sinh" :value="formatDateYMDToDMY(studentInfo?.date_of_birth)">
          <template #icon>
            <Calendar class="size-4 text-[var(--color-secondary)]" />
          </template>
        </InfoRow>
      </div>
      <div class="space-y-4 col-span-1">
        <InfoRow label="Vai trò" :value="'Học viên'">
          <template #icon>
            <UserRoundCog class="size-4 text-[var(--color-primary)]" />
          </template>
        </InfoRow>
        <InfoRow label="Ngày tham gia" :value="formatDateYMDToDMY(studentInfo?.joining_date)">
          <template #icon>
            <Calendar1 class="size-4 text-[var(--color-secondary)]" />
          </template>
        </InfoRow>
        <InfoRow label="Giới tính" :value="studentInfo?.gender">
          <template #icon>
            <VenusAndMars class="size-4 text-[var(--color-primary)]" />
          </template>
        </InfoRow>
        <InfoRow label="Quốc tịch" :value="studentInfo?.nationality">
          <template #icon>
            <Flag class="size-4 text-[var(--color-secondary)]" />
          </template>
        </InfoRow>
        <InfoRow label="Địa chỉ 1"
          :value="studentInfo?.address_line_1">
          <template #icon>
            <MapPin class="size-4 text-[var(--color-primary)] shrink-0" />
          </template>
        </InfoRow>
        <InfoRow label="Địa chỉ 2" :value="studentInfo?.address_line_2">
          <template #icon>
            <MapPin class="size-4 text-[var(--color-secondary)]" />
          </template>
        </InfoRow>
      </div>
    </div>
  </div>
</template>

<script setup>
import InfoRow from '@/components/profile/InfoRow.vue'
import { User, UserRoundCog, Mail, Phone, Calendar, Flag, IdCard, VenusAndMars, Calendar1, MapPin } from 'lucide-vue-next'
import { formatDateYMDToDMY } from '@/utils/date'

const props = defineProps({
  studentInfo: {
    type: Object,
    required: true,
  },
  user: {
    type: Object,
    required: false,
    default: () => ({}),
  },
})
</script>

<style scoped></style>
