<template>
  <div class="shell">
    <header>
      <div>
        <h1>深度教学助手</h1>
        <small>ChatGPT 风格 · Mock 数据</small>
      </div>
      <span class="badge">预览模式</span>
    </header>

    <QuickActions :actions="quickActions" @select="handleQuickAction" />

    <MessageList :messages="messages" />

    <div class="input-bar">
      <form @submit.prevent="submit">
        <textarea
          v-model="input"
          placeholder="告诉助手：出题 / 题库概览 / 班级情况 / 分配题目..."
        ></textarea>
        <button type="submit">发送</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import QuickActions from './components/QuickActions.vue';
import MessageList from './components/MessageList.vue';
import {
  generateMockQuestions,
  mockOverview,
  mockClasses,
  mockStudents,
  mockTopics
} from './data/mock.js';

const messages = ref([]);
const input = ref('');
const quickActions = [
  { label: '出题示例', prompt: '请出 5 道函数题' },
  { label: '题库概览', prompt: '展示题库结构概览' },
  { label: '班级/学生管理', prompt: '列出班级和学生情况' },
  { label: '分配题目', prompt: '给三班学生布置作业' }
];

let messageId = 0;

function pushMessage(role, text, payload) {
  messages.value.push({
    id: ++messageId,
    role,
    text,
    payload
  });
}

function submit() {
  if (!input.value.trim()) return;
  handlePrompt(input.value.trim());
  input.value = '';
}

function handleQuickAction(prompt) {
  handlePrompt(prompt);
}

function handlePrompt(prompt) {
  pushMessage('user', prompt);
  setTimeout(() => respond(prompt), 200);
}

function respond(prompt) {
  const normalized = prompt.toLowerCase();
  if (prompt.includes('出') && prompt.includes('题')) {
    pushMessage('assistant', '根据你的指令生成了题目草稿：', {
      type: 'questions',
      questions: generateMockQuestions()
    });
    return;
  }
  if (prompt.includes('题库') || prompt.includes('概览') || prompt.includes('结构')) {
    pushMessage('assistant', '当前题库统计如下：', {
      type: 'overview',
      overview: mockOverview
    });
    return;
  }
  if (prompt.includes('班级') || prompt.includes('学生')) {
    pushMessage('assistant', '班级与学生情况如下：', {
      type: 'classes',
      classes: mockClasses,
      students: mockStudents
    });
    return;
  }
  if (normalized.includes('分配') || normalized.includes('布置')) {
    pushMessage('assistant', '请选择班级与学生，生成分配任务：', {
      type: 'assign',
      classes: mockClasses,
      students: mockStudents,
      topics: mockTopics
    });
    return;
  }
  pushMessage('assistant', '我可以帮你出题、查看题库、管理班级/学生或分配题目。');
}

pushMessage('assistant', '你好，我是教学助手。可以随时告诉我需求。');
</script>

<style scoped>
.shell {
  width: min(1200px, 100%);
  margin: 0 auto;
  background: #ffffff;
  min-height: 90vh;
  border-radius: 24px;
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
header {
  padding: 18px 28px;
  background: linear-gradient(135deg, #2563eb, #0f62fe);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
header h1 {
  margin: 0;
  font-size: 20px;
}
.badge {
  font-size: 12px;
  background: #bfdbfe;
  color: #1d4ed8;
  padding: 3px 10px;
  border-radius: 999px;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #f5f7fb;
}
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 18px;
}
.message.user {
  flex-direction: row-reverse;
}
.bubble {
  max-width: 75%;
  padding: 14px 18px;
  border-radius: 20px;
  line-height: 1.5;
  font-size: 15px;
}
.message.assistant .bubble {
  background: white;
  border: 1px solid #dbeafe;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.08);
}
.message.user .bubble {
  background: #2563eb;
  color: white;
}
.cards {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}
.card {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px;
  background: white;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.input-bar {
  border-top: 1px solid #e2e8f0;
  padding: 18px;
  background: #fff;
}
.input-bar form {
  display: flex;
  gap: 12px;
}
.input-bar textarea {
  flex: 1;
  resize: none;
  border-radius: 16px;
  border: 1px solid #cbd5f5;
  padding: 12px 16px;
  font-size: 15px;
  min-height: 60px;
}
.input-bar button {
  border: none;
  border-radius: 16px;
  background: #2563eb;
  color: white;
  padding: 0 26px;
  font-size: 15px;
}
</style>
