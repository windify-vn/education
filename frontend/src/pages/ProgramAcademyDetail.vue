<script setup>
import ProgramAcademyDetail from '../components/programs-academy/ProgramAcademyDetail.vue';
import { useRoute } from 'vue-router'

const route = useRoute()
const programName = route.params.programName

</script>

<template>
  <div class="p-5 space-y-6">
    <p>{{ programName }}</p>
    <ProgramAcademyDetail :programName="programName" />
  </div>
</template>