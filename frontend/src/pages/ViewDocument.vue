<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const documentName = route.params.documentName
</script>

<template>
  <div class="p-5 space-y-6">
    <p>View Document</p>
  </div>
</template>