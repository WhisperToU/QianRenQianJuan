<template>
  <div class="chat-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <aside v-if="!sidebarCollapsed" class="sidebar">
      <div class="sidebar-top">
        <div class="sidebar-controls">
          <button
            class="collapse-toggle"
            type="button"
            @click="toggleSidebar"
            aria-label="收起菜单"
          >
            <span class="icon">⟵</span>
            <span>收起菜单</span>
          </button>
          <button class="new-chat" type="button" @click="startNewConversation">
            <span>+ 新建会话</span>
          </button>
        </div>
        <div class="conversation-label">会话记录</div>
        <div class="conversation-list">
          <button
            v-for="conversation in conversations"
            :key="conversation.id"
            type="button"
            :class="['conversation-item', { active: conversation.id === selectedConversation }]"
            @click="selectConversation(conversation.id)"
          >
            <span>{{ conversation.title }}</span>
            <small>{{ conversation.updated }}</small>
          </button>
        </div>
      </div>
      <div class="sidebar-bottom">
        <button type="button" class="user-card">
          <div class="avatar">访</div>
          <div>
            <strong>访客用户</strong>
            <small>未登录</small>
          </div>
        </button>
        <button type="button" class="login-btn">登录账号</button>
      </div>
    </aside>
    <div v-else class="sidebar-rail">
      <button
        type="button"
        class="rail-btn"
        aria-label="展开菜单"
        @click="toggleSidebar"
      >
        ☰
      </button>
      <button
        type="button"
        class="rail-btn rail-new"
        aria-label="新建会话"
        @click="startNewConversation"
      >
        +
      </button>
    </div>

    <main class="chat-surface">
      <header class="surface-header">
        <h1>深度教学助手</h1>
      </header>

      <section class="chat-window">
        <MessageList :messages="messages" />
      </section>

      <section class="quick-bar">
        <QuickActions :actions="quickActions" @select="handleQuickAction" />
      </section>

      <div class="composer">
        <form @submit.prevent="submit">
          <textarea
            v-model="input"
            placeholder="告诉助手：出题 / 题库概览 / 班级情况 / 分配题目..."
          ></textarea>
          <button type="submit" :disabled="!input.trim()">发送</button>
        </form>
        <small>Shift + Enter 换行 · Enter 发送</small>
      </div>
    </main>
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

const conversationCache = new Map();

const conversations = ref([
  { id: 1, title: '深度教学助手', updated: '刚刚' },
  { id: 2, title: '题库概览演示', updated: '今天' },
  { id: 3, title: '班级管理试用', updated: '昨天' }
]);

const selectedConversation = ref(conversations.value[0]?.id ?? null);
const messages = ref([]);
const input = ref('');
const sidebarCollapsed = ref(false);
const quickActions = [
  { label: '出题示例', prompt: '请出 5 道函数题', type: 'questions' },
  { label: '题库概览', prompt: '展示题库结构概览', type: 'overview' },
  { label: '班级/学生管理', prompt: '列出班级和学生情况', type: 'classes' },
  { label: '分配题目', prompt: '给三班学生布置作业', type: 'assign' }
];

let messageId = 0;

if (selectedConversation.value !== null) {
  initConversation(selectedConversation.value);
}

function initConversation(id) {
  messages.value = [];
  conversationCache.set(id, messages.value);
  seedGreeting();
}

function seedGreeting() {
  pushMessage('assistant', '你好，我是教学助手，可以像 ChatGPT 一样向我提问。');
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value;
}

function startNewConversation() {
  const id = Date.now();
  conversations.value.unshift({
    id,
    title: `新会话 ${conversations.value.length + 1}`,
    updated: '刚刚'
  });
  selectConversation(id, { reset: true });
}

function selectConversation(id, { reset = false } = {}) {
  if (selectedConversation.value === id && !reset) return;
  if (selectedConversation.value !== null) {
    conversationCache.set(selectedConversation.value, messages.value);
  }
  selectedConversation.value = id;
  if (!reset && conversationCache.has(id)) {
    messages.value = conversationCache.get(id);
  } else {
    initConversation(id);
  }
}

function pushMessage(role, text, payload) {
  messages.value = [
    ...messages.value,
    {
      id: ++messageId,
      role,
      text,
      payload
    }
  ];
  if (selectedConversation.value !== null) {
    conversationCache.set(selectedConversation.value, messages.value);
  }
}

function submit() {
  if (!input.value.trim()) return;
  handlePrompt(input.value.trim());
  input.value = '';
}

function handleQuickAction(action) {
  handlePrompt(action.prompt, action.type);
}

function handlePrompt(prompt, intent) {
  pushMessage('user', prompt);
  touchConversation();
  setTimeout(() => respond(prompt, intent), 200);
}

function respond(prompt, intent) {
  const normalized = prompt.toLowerCase();

  if (intent === 'questions' || prompt.includes('出题') || prompt.includes('题目')) {
    pushMessage('assistant', '根据你的指令生成了题目草稿：', {
      type: 'questions',
      questions: generateMockQuestions()
    });
    touchConversation();
    return;
  }

  if (intent === 'overview' || prompt.includes('题库') || prompt.includes('概览') || prompt.includes('结构')) {
    pushMessage('assistant', '当前题库统计如下：', {
      type: 'overview',
      overview: mockOverview
    });
    touchConversation();
    return;
  }

  if (intent === 'classes' || prompt.includes('班级') || prompt.includes('学生')) {
    pushMessage('assistant', '班级与学生情况如下：', {
      type: 'classes',
      classes: mockClasses,
      students: mockStudents
    });
    touchConversation();
    return;
  }

  if (
    intent === 'assign' ||
    prompt.includes('分配') ||
    prompt.includes('布置') ||
    normalized.includes('assign')
  ) {
    pushMessage('assistant', '请选择班级与学生，生成分配任务：', {
      type: 'assign',
      classes: mockClasses,
      students: mockStudents,
      topics: mockTopics
    });
    touchConversation();
    return;
  }

  pushMessage('assistant', '我可以帮你出题、查看题库结构、管理班级学生或分配题目。');
  touchConversation();
}

function touchConversation(label = '刚刚') {
  const convo = conversations.value.find((c) => c.id === selectedConversation.value);
  if (convo) convo.updated = label;
}
</script>

<style scoped>
.chat-shell {
  min-height: 100vh;
  padding: 0;
  background: radial-gradient(circle at top, rgba(59, 130, 246, 0.18), transparent 55%),
    radial-gradient(circle at 20% 20%, rgba(14, 165, 233, 0.12), transparent 40%),
    #030712;
  color: #ececf1;
  display: flex;
  gap: 0;
  align-items: stretch;
}

.chat-shell.sidebar-collapsed {
  padding-left: 0;
}

.sidebar {
  width: 280px;
  flex-shrink: 0;
  background: rgba(15, 23, 42, 0.96);
  border-right: 1px solid rgba(148, 163, 184, 0.2);
  padding: 18px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: none;
  height: 100vh;
  position: sticky;
  top: 0;
}

.sidebar-top {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sidebar-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.new-chat {
  width: 100%;
  padding: 12px;
  border-radius: 14px;
  border: 1px dashed rgba(148, 163, 184, 0.5);
  background: rgba(30, 41, 59, 0.7);
  color: #e0e7ff;
  font-size: 14px;
  cursor: pointer;
}

.collapse-toggle {
  width: 100%;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 14px;
  padding: 10px 12px;
  background: rgba(15, 23, 42, 0.6);
  color: #e2e8f0;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.collapse-toggle .icon {
  font-size: 16px;
}

.sidebar-rail {
  width: 70px;
  flex-shrink: 0;
  background: rgba(15, 23, 42, 0.95);
  border-right: 1px solid rgba(148, 163, 184, 0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 16px 10px;
  height: 100vh;
  position: sticky;
  top: 0;
}

.rail-btn {
  width: 100%;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 14px;
  background: rgba(30, 41, 59, 0.8);
  color: #e2e8f0;
  padding: 10px 0;
  font-size: 18px;
  cursor: pointer;
}

.rail-new {
  font-size: 22px;
  border-style: dashed;
}

.conversation-label {
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(148, 163, 184, 0.9);
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

.conversation-item {
  width: 100%;
  border: 1px solid transparent;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.5);
  color: #f8fafc;
  text-align: left;
  padding: 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.conversation-item small {
  color: rgba(148, 163, 184, 0.8);
}

.conversation-item.active {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(37, 99, 235, 0.15);
}

.sidebar-bottom {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-card {
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 16px;
  padding: 10px 12px;
  background: rgba(15, 23, 42, 0.6);
  color: inherit;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.login-btn {
  border: none;
  border-radius: 14px;
  padding: 12px;
  background: linear-gradient(135deg, #22d3ee, #a855f7);
  color: #030712;
  font-weight: 600;
  cursor: pointer;
}

.chat-surface {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
  margin-left: 0;
  min-height: 100vh;
  height: 100vh;
  overflow: hidden;
}

.surface-header,
.chat-window,
.quick-bar,
.composer {
  background: rgba(32, 33, 35, 0.96);
  border-left: 1px solid rgba(255, 255, 255, 0.05);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0;
  box-shadow: none;
}

.surface-header {
  padding: 18px 22px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.surface-header h1 {
  margin: 0;
  font-size: clamp(22px, 3vw, 30px);
}

.quick-bar {
  padding: 10px 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  border-bottom: none;
}

.quick-bar :deep(.quick-actions) {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
}

.quick-bar :deep(button) {
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.45);
  color: #e0e7ff;
  padding: 12px 14px;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.quick-bar :deep(button:hover) {
  border-color: rgba(248, 250, 252, 0.5);
  transform: translateY(-1px);
}

.chat-window {
  flex: 1;
  padding: 18px 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.chat-window :deep(.messages) {
  flex: 1;
  padding: 0 28px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.4) transparent;
}

.chat-window :deep(.messages::-webkit-scrollbar) {
  width: 8px;
}

.chat-window :deep(.messages::-webkit-scrollbar-track) {
  background: transparent;
}

.chat-window :deep(.messages::-webkit-scrollbar-thumb) {
  background: rgba(148, 163, 184, 0.35);
  border-radius: 999px;
}
.chat-window :deep(.message) {
  display: flex;
  gap: 16px;
}

.chat-window :deep(.message.user) {
  justify-content: flex-end;
}

.chat-window :deep(.bubble) {
  max-width: 80%;
  padding: 14px 18px;
  border-radius: 20px;
  border: 1px solid transparent;
  line-height: 1.6;
  font-size: 15px;
}

.chat-window :deep(.message.assistant .bubble) {
  background: #444654;
  border-color: rgba(168, 85, 247, 0.25);
  color: #f3f4f6;
}

.chat-window :deep(.message.user .bubble) {
  background: #1f1f24;
  border-color: rgba(148, 163, 184, 0.2);
  color: #f8fafc;
}

.chat-window :deep(.bubble component) {
  display: block;
  margin-top: 12px;
}

.composer {
  padding: 12px 18px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  position: sticky;
  bottom: 0;
  z-index: 2;
  flex-shrink: 0;
}

.composer form {
  display: flex;
  gap: 8px;
  align-items: center;
}

.composer textarea {
  flex: 1;
  resize: none;
  min-height: 70px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(3, 7, 18, 0.6);
  color: #f8fafc;
  padding: 10px 12px;
  font-size: 15px;
  line-height: 1.5;
  font-family: inherit;
}

.composer textarea:focus {
  outline: none;
  border-color: rgba(236, 72, 153, 0.6);
  box-shadow: 0 0 0 1px rgba(236, 72, 153, 0.15);
}

.composer button {
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #22d3ee, #a855f7);
  color: #0f172a;
  font-weight: 600;
  padding: 10px 18px;
  cursor: pointer;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.composer button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.composer button:not(:disabled):hover {
  transform: translateY(-1px);
}

.composer small {
  font-size: 11px;
  color: rgba(148, 163, 184, 0.75);
}

@media (max-width: 700px) {
  .surface-header,
  .composer form {
    flex-direction: column;
    align-items: flex-start;
  }

  .chat-window :deep(.bubble) {
    max-width: 100%;
  }
}
</style>
