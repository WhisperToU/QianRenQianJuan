<template>
  <div class="quick-actions">
    <button
      v-for="action in actions"
      :key="action.label"
      type="button"
      @click="$emit('select', action.prompt)"
    >
      {{ action.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  actions: {
    type: Array,
    required: true
  }
});
defineEmits(['select']);
</script>
