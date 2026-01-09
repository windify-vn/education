<script setup>
import { studentStore } from '@/stores/student'
import ProgramAccordion from '../components/programs-academy/ProgramAccordion.vue';

const { studentInfo } = studentStore()
</script>

<style scoped></style>

<template>
  <div class="p-5 space-y-6">
    <ProgramAccordion :studentName="studentInfo?.name" :openAll="true" />
  </div>
</template>
