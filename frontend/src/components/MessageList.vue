<template>
  <div class="messages" ref="messageContainer">
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
import { nextTick, ref, watch } from 'vue';
import QuestionCards from './QuestionCards.vue';
import OverviewCard from './OverviewCard.vue';
import ClassCard from './ClassCard.vue';
import AssignCard from './AssignCard.vue';
import SourceQuestionCard from './SourceQuestionCard.vue';
import TopicCard from './TopicCard.vue';

const props = defineProps({
  messages: {
    type: Array,
    required: true
  }
});

const messageContainer = ref(null);

const componentMap = {
  questions: QuestionCards,
  overview: OverviewCard,
  classes: ClassCard,
  assign: AssignCard,
  source_question: SourceQuestionCard,
  topic: TopicCard
};

watch(
  () => props.messages.length,
  () => {
    nextTick(() => {
      if (!messageContainer.value) return;
      messageContainer.value.scrollTo({
        top: messageContainer.value.scrollHeight,
        behavior: 'smooth'
      });
    });
  }
);
</script>
