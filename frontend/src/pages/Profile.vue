<template>
  <div class="p-5 space-y-6">
    <!-- Profile Header and Info Card -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <ProfileHeader :studentInfo="studentInfo" :user="user" />
      <ProfileInfoCard :studentInfo="studentInfo" :user="user" />
    </div>

    <!-- Chương trình đang tham gia -->
    <div class="grid grid-cols-1 gap-6">
      <ProgramAccordion :studentName="studentInfo?.name" />
    </div>

    <!-- Achievement -->
    <div class="grid grid-cols-1 gap-6">
      <Achievement :studentName="studentInfo?.name" @view-progress="onViewProgress" />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { usersStore } from '@/stores/user'
import { studentStore } from '@/stores/student'
import ProfileInfoCard from '@/components/profile/ProfileInfoCard.vue'
import Achievement from '../components/profile/Achievement.vue'
import ProfileHeader from '@/components/profile/ProfileHeader.vue'
import ProgramAccordion from '../components/programs-academy/ProgramAccordion.vue'

const { user } = usersStore()
const { student, studentInfo } = studentStore()

// Header logic moved to ProfileHeader component

onMounted(async () => {
  if (!studentInfo?.name) {
    try {
      await student.submit()
    } catch (e) {
      console.error(e)
    }
  }
  // ProgramAccordion sẽ tự gọi API theo studentName
})

function onViewProgress() {
  // TODO: navigate to progress page when available
  console.log('View progress clicked')
}
</script>