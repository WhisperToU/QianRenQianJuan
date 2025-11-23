<template>
  <div class="messages" ref="messageContainer">
    <div
      v-for="message in messages"
      :key="message.id"
      :class="['message', message.role]"
    >
      <div class="bubble">
        <!-- 文本内容 -->
        <p v-if="message.text" style="margin: 0 0 8px">{{ message.text }}</p>

        <!-- 渲染卡片组件 -->
        <component
          v-if="isValidPayload(message.payload)"
          :is="componentMap[message.payload.type]"
          :payload="message.payload"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';

/* ----------------------------------------
 *  引入你的卡片组件（目前你给我上传的只有 ClassCard）
 * ---------------------------------------- */
import ClassCard from './ClassCard.vue'
import SourceQuestionCard from './SourceQuestionCard.vue'
import TopicCard from './TopicCard.vue'
import QuestionCards from './QuestionCards.vue'
import AssignCard from './AssignCard.vue'
import OverviewCard from './OverviewCard.vue'


/* ----------------------------------------
 *  卡片类型映射
 *  只要后端返回的 payload.type 符合这些 key，就会渲染对应组件
 * ---------------------------------------- */
const componentMap = {
  class: ClassCard,
  classes: ClassCard,
  student: ClassCard,
  source_question: SourceQuestionCard,
  topic: TopicCard,
  question: QuestionCards,
  questions: QuestionCards,
  assign: AssignCard,
  overview: OverviewCard,
}

const props = defineProps({
  messages: { type: Array, default: () => [] }
});

const messageContainer = ref(null);

/* 自动滚动到底部 */
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

function isValidPayload(payload) {
  if (!payload) return false;
  if (typeof payload !== 'object') return false;
  if (!payload.type) return false;
  if (!componentMap[payload.type]) return false;
  return true;
}

</script>

<style scoped>
.messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.message {
  display: flex;
  gap: 16px;
}
.bubble {
  max-width: 80%;
  padding: 14px 18px;
  border-radius: 20px;
  border: 1px solid transparent;
  line-height: 1.6;
  font-size: 15px;
}
</style>
