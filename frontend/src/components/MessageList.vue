<template>
  <div class="messages">
    <div
      v-for="message in messages"
      :key="message.id"
      :class="['message', message.role]"
    >
      <div class="bubble">
        <p style="margin: 0 0 8px">{{ message.text }}</p>
        <component
          v-if="message.payload?.type"
          :is="componentMap[message.payload.type]"
          :payload="message.payload"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import QuestionCards from './QuestionCards.vue';
import OverviewCard from './OverviewCard.vue';
import ClassCard from './ClassCard.vue';
import AssignCard from './AssignCard.vue';

defineProps({
  messages: {
    type: Array,
    required: true
  }
});

const componentMap = {
  questions: QuestionCards,
  overview: OverviewCard,
  classes: ClassCard,
  assign: AssignCard
};
</script>
