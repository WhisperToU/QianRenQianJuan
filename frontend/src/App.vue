<template>
  <div class="chat-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- 侧边栏 -->
    <aside v-if="!sidebarCollapsed" class="sidebar">
      <div class="sidebar-top">
        <div class="sidebar-controls">
          <button class="collapse-toggle" type="button" @click="toggleSidebar" aria-label="关闭侧边栏">
            <span class="icon">✖</span>
          </button>
          <button class="new-chat" type="button" @click="startNewConversation" aria-label="新对话">
            <span>+</span>
          </button>
        </div>

        <div class="conversation-label">会话记录</div>

        <div class="conversation-list">
          <div
            v-for="conversation in conversations"
            :key="conversation.id"
            class="conversation-item"
            :class="{ active: conversation.id === selectedConversation }"
          >
            <button
              class="conversation-delete"
              type="button"
              title="删除会话"
              @click.stop="removeConversation(conversation.id)"
            >
              ✖
            </button>

            <button class="conversation-link" type="button" @click="selectConversation(conversation.id)">
              <span>{{ conversation.title }}</span>
              <small>{{ conversation.updated }}</small>
            </button>
          </div>
        </div>
      </div>

      <div class="sidebar-bottom">
        <template v-if="isAuthenticated">
          <div class="account-row">
            <div class="avatar-chip">
              <span>{{ sidebarProfile.avatarFallback }}</span>
            </div>
            <button type="button" class="logout-btn" @click="handleAuthButtonClick">退出登录</button>
          </div>
        </template>

        <template v-else>
          <button type="button" class="login-btn" @click="handleAuthButtonClick">登录账号</button>
        </template>
      </div>
    </aside>

    <!-- 折叠侧边栏 -->
    <div v-else class="sidebar-rail">
      <button type="button" class="rail-btn" aria-label="展开菜单" @click="toggleSidebar">☰</button>
      <button type="button" class="rail-btn rail-new" aria-label="新对话" @click="startNewConversation">+</button>
      <button
        type="button"
        class="rail-avatar"
        :title="sidebarProfile.name"
        @click="toggleSidebar"
      >
        <div class="avatar avatar-image" v-if="sidebarProfile.avatarUrl">
          <img :src="sidebarProfile.avatarUrl" :alt="sidebarProfile.name" />
        </div>
        <div class="avatar avatar-guest" v-else>
          <span>{{ sidebarProfile.avatarFallback }}</span>
        </div>
      </button>
    </div>

    <!-- 主界面 -->
    <main class="chat-surface">
      <header class="surface-header">
        <h1>教学助手</h1>
      </header>

      <section class="chat-window">
        <MessageList :messages="messages" />
      </section>

      <div class="composer">
        <form @submit.prevent="submit">
          <div class="composer-field">
            <textarea
              ref="composerRef"
              v-model="input"
              placeholder="询问任何问题"
              @keydown="handleComposerKeydown"
              @input="adjustComposerHeight"
              rows="1"
            ></textarea>

            <button type="submit" :disabled="!input.trim() || isThinking" aria-label="发送消息">
              <span aria-hidden="true">✈</span>
            </button>
          </div>
        </form>
      </div>

      <!-- 登录窗口 -->
      <AuthModal
        v-if="showAuth"
        :mode="authMode"
        :loading="authLoading"
        :error="authError"
        @mode-change="(m) => (authMode = m)"
        @close="closeAuth"
        @submit="handleAuthSubmit"
      />
    </main>
  </div>
</template>

<script setup>
/* ---------------- imports ---------------- */
import { computed, ref, watch, nextTick } from 'vue';
import MessageList from './components/MessageList.vue';
import AuthModal from './components/AuthModal.vue';
import { apiFetch } from './utils/api';

/* ---------------- 基础状态 ---------------- */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
const conversationCache = new Map();

const currentUser = ref(null);
const showAuth = ref(false);
const authMode = ref('login');
const authLoading = ref(false);
const authError = ref('');

const isThinking = ref(false);
const composerRef = ref(null);

const guestProfile = {
  name: '游客用户',
  status: '未登录',
  avatarFallback: '客'
};

const sidebarProfile = computed(() => {
  if (!currentUser.value) return guestProfile;
  const name = currentUser.value.name ?? '';
  return {
    name,
    avatarUrl: currentUser.value.avatarUrl || '',
    avatarFallback: (name.trim()?.slice(-1)) || '客'
  };
});

const isAuthenticated = computed(() => Boolean(currentUser.value));

/* ---------------- 会话 ---------------- */
const conversations = ref([]);
const selectedConversation = ref(null);
const messages = ref([]);
const input = ref('');
const sidebarCollapsed = ref(true);

let messageId = 0;
let greetingTimer = null;

/* ---------------- 登录变化监听 ---------------- */
watch(isAuthenticated, (logged, prev) => {
  if (prev !== undefined && logged !== prev) {
    scheduleGreeting();
    if (logged) sidebarCollapsed.value = true;
    if (logged) loadConversations();
    else {
      conversations.value = [];
      selectedConversation.value = null;
    }
  }
}, { immediate: true });

loadConversations();

/* ---------------- 加载会话 ---------------- */
async function loadConversations() {
  if (!isAuthenticated.value) {
    conversations.value = [];
    selectedConversation.value = null;
    return;
  }

  try {
    const data = await apiFetch('/conversations/list');
    conversations.value = (data || []).map((item) => ({
      id: item.conversation_id,
      title: item.title,
      updated: item.updated_at
    }));

    if (!selectedConversation.value && conversations.value.length) {
      selectConversation(conversations.value[0].id, { reset: true });
    }

    if (!conversations.value.length) await startNewConversation();
  } catch (error) {
    console.error('加载会话失败', error);
  }
}

/* ---------------- 加载消息 ---------------- */
async function loadMessages(conversationId) {
  if (!isAuthenticated.value || !conversationId) return;

  try {
    const data = await apiFetch(`/conversations/${conversationId}/messages`);

    messages.value = (data || []).map((item) => ({
      id: item.message_id,
      role: item.sender === 'user' ? 'user' : 'assistant',
      text: item.content,
      payload: null,
      timestamp: item.timestamp
    }));

    conversationCache.set(conversationId, messages.value);
  } catch (error) {
    console.error('加载消息失败', error);
  }
}

/* ---------------- 初始化新对话 ---------------- */
function initConversation(id) {
  messages.value = [];
  conversationCache.set(id, messages.value);
  scheduleGreeting();
}

/* ---------------- 问候语 ---------------- */
function scheduleGreeting() {
  if (greetingTimer) clearTimeout(greetingTimer);

  greetingTimer = setTimeout(() => {
    const isLogged = isAuthenticated.value;
    const text = isLogged
      ? `${currentUser.value?.name || '老师'}，您好`
      : '请登录以继续使用教学助手';
    pushMessage('assistant', text);
    greetingTimer = null;
  }, 800);
}

/* ---------------- 侧边栏 ---------------- */
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value;
}

/* ---------------- 登录模块 ---------------- */
function openAuth(mode = 'login') {
  authMode.value = mode;
  authError.value = '';
  showAuth.value = true;
}

async function handleAuthButtonClick() {
  if (isAuthenticated.value) {
    await logout();
    return;
  }
  openAuth('login');
}

function closeAuth() {
  showAuth.value = false;
  authError.value = '';
}

async function handleAuthSubmit(payload) {
  const { mode, identifier, password, school_name, group_name } = payload;

  authError.value = '';
  authLoading.value = true;

  try {
    const resp = await fetch(`${API_BASE_URL}/auth/${mode}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        identifier,
        password,
        school_name,
        group_name
      })
    });

    const data = await resp.json();
    if (!resp.ok) throw new Error(data?.error || '请求失败');

    if (data.token) localStorage.setItem('auth_token', data.token);

    currentUser.value = {
      name: data.user.username,
      avatarUrl: data.user.avatarUrl,
      status: '已登录',
      ...data.user
    };

    showAuth.value = false;
  } catch (error) {
    authError.value = error?.message || '登录失败';
  } finally {
    authLoading.value = false;
  }
}

async function logout() {
  localStorage.removeItem('auth_token');
  currentUser.value = null;
  conversations.value = [];
  selectedConversation.value = null;
  messages.value = [];
  conversationCache.clear();
}

/* ---------------- 创建/删除 会话 ---------------- */
async function startNewConversation() {
  if (isAuthenticated.value) {
    const resp = await apiFetch('/conversations/', {
      method: 'POST',
      body: JSON.stringify({ title: '新对话' })
    });

    const newConversation = {
      id: resp.conversation_id,
      title: resp.title,
      updated: new Date().toISOString()
    };

    conversations.value.unshift(newConversation);
    selectConversation(newConversation.id, { reset: true });
    return;
  }

  const id = Date.now();
  conversations.value.unshift({
    id,
    title: `新对话 ${conversations.value.length + 1}`,
    updated: '刚刚'
  });
  selectConversation(id, { reset: true });
}

async function removeConversation(id) {
  const idx = conversations.value.findIndex((c) => c.id === id);
  if (idx === -1) return;

  if (isAuthenticated.value) {
    await apiFetch(`/conversations/${id}`, { method: 'DELETE' });
  }

  const wasSelected = selectedConversation.value === id;
  conversations.value.splice(idx, 1);

  if (wasSelected) {
    if (conversations.value.length) selectConversation(conversations.value[0].id, { reset: true });
    else await startNewConversation();
  }
}

/* ---------------- 选择会话 ---------------- */
function selectConversation(id, { reset = false } = {}) {
  if (selectedConversation.value === id && !reset) return;

  if (selectedConversation.value !== null) {
    conversationCache.set(selectedConversation.value, messages.value);
  }

  selectedConversation.value = id;

  if (isAuthenticated.value) {
    loadMessages(id);
    return;
  }

  if (!reset && conversationCache.has(id)) messages.value = conversationCache.get(id);
  else initConversation(id);
}

/* ---------------- 聊天消息操作 ---------------- */
function pushMessage(role, text, payload = null) {
  const id = ++messageId;
  messages.value = [
    ...messages.value,
    { id, role, text, payload }
  ];

  if (selectedConversation.value !== null) {
    conversationCache.set(selectedConversation.value, messages.value);
  }

  return id;
}

function updateMessage(id, partial) {
  messages.value = messages.value.map(msg =>
    msg.id === id ? { ...msg, ...partial } : msg
  );
}

/* ---------------- 输入框 ---------------- */
function submit() {
  if (!input.value.trim()) return;
  handlePrompt(input.value.trim());
  input.value = '';
  nextTick(() => resetComposerHeight());
}

function handleComposerKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    submit();
  }
}

function adjustComposerHeight() {
  const el = composerRef.value;
  if (!el) return;

  el.style.height = 'auto';
  const lineHeight = parseFloat(getComputedStyle(el).lineHeight) || 20;
  const maxHeight = lineHeight * 5;
  const targetHeight = Math.min(el.scrollHeight, maxHeight);

  el.style.height = `${targetHeight}px`;
  el.style.overflowY = el.scrollHeight > maxHeight ? 'auto' : 'hidden';
}

function resetComposerHeight() {
  const el = composerRef.value;
  if (!el) return;

  el.style.height = 'auto';
  el.style.overflowY = 'hidden';
}

/* ---------------- 聊天主流程 ---------------- */
async function handlePrompt(prompt) {
  pushMessage('user', prompt);
  touchConversation();
  sendMessageToBackend('user', prompt);
  await respond(prompt);
}

async function respond(prompt) {
  if (isThinking.value) return;

  isThinking.value = true;
  const placeholderId = pushMessage('assistant', '正在生成回复...', { loading: true });
  touchConversation('处理中');

  try {
    const result = await sendPrompt(prompt);
    const mode = result?.mode || 'chat';

    if (mode === 'chat') {
      updateMessage(placeholderId, { text: result.text, payload: null });
      touchConversation('刚刚');
      return;
    }

    /* ---------------- CRUD 卡片模式 ---------------- */
    const payload = normalizeCrudPayload(result.data || {});
    console.log("DEBUG payload from AI:", payload);
    const messageText =
      payload.message ||
      result.text ||
      '(来自 AI 的卡片响应)';

    const type = normalizeCardType(payload.target || payload.type);

    // 修改消息，使其包含卡片
    updateMessage(placeholderId, {
      text: messageText,
      payload: {
        type,
        ...payload
      }
    });

    touchConversation('卡片');
  } catch (err) {
    updateMessage(placeholderId, {
      text: `生成时出错：${err?.message || err}`,
      payload: { error: true }
    });
  } finally {
    isThinking.value = false;
  }
}

/* ---------------- 辅助函数 ---------------- */
function sendMessageToBackend(role, text) {
  if (!isAuthenticated.value || !selectedConversation.value || !text) return;

  apiFetch(`/conversations/${selectedConversation.value}/messages`, {
    method: 'POST',
    body: JSON.stringify({ sender: role, content: text })
  });
}

function touchConversation(label = '刚刚') {
  const c = conversations.value.find(c => c.id === selectedConversation.value);
  if (c) c.updated = label;
}

function normalizeCardType(str) {
  if (!str) return '';
  return str.trim().toLowerCase().replace(/\s+/g, '_');
}

function buildQuestionPreview(fields = {}) {
  const pick = (...keys) => {
    for (const key of keys) {
      const value = fields[key];
      if (value !== undefined && value !== null && value !== '') {
        return value;
      }
    }
    return '';
  };

  const normalizeDifficulty = (value) => {
    if (!value) return 'medium';
    const text = String(value).toLowerCase();
    if (text.includes('easy') || text.includes('简单')) return 'easy';
    if (text.includes('hard') || text.includes('difficult') || text.includes('难')) return 'difficult';
    return 'medium';
  };

  return {
    question: pick('question_text', 'question', 'content'),
    answer: pick('answer_text', 'answer'),
    topic: pick('topic', 'topic_name'),
    topic_id: fields.topic_id ?? null,
    difficulty: normalizeDifficulty(pick('difficulty_level', 'difficulty')),
    type: fields.type || 'question',
    duration: fields.duration,
    imageUrl: pick('question_image', 'imageUrl')
  };
}

function normalizeCrudPayload(payload = {}) {
  if (!payload || typeof payload !== 'object') return {};
  const normalized = { ...payload };
  normalized.fields = normalized.fields || {};
  normalized.defaults = normalized.defaults || normalized.fields;

  if (normalizeCardType(normalized.target || normalized.type) === 'question') {
    normalized.questions = Array.isArray(normalized.questions) && normalized.questions.length
      ? normalized.questions
      : [buildQuestionPreview(normalized.fields)];
    normalized.topicOptions = normalized.topicOptions || [];
  }

  return normalized;
}

/* ---------------- AI 请求 ---------------- */
async function sendPrompt(prompt) {
  const payload = JSON.stringify({ prompt });

  if (isAuthenticated.value) {
    return apiFetch('/ai/secure/generate', {
      method: 'POST',
      body: payload
    });
  }

  const resp = await fetch(`${API_BASE_URL}/ai/public/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: payload
  });

  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.error || '请求失败');

  return { mode: 'chat', text: data.text };
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
  position: relative;
  padding-top: 12px;
}

.new-chat {
  width: 46px;
  height: 50px;
  border-radius: 10px;
  border: 1px dashed rgba(148, 163, 184, 0.5);
  background: rgba(30, 41, 59, 0.7);
  color: #e0e7ff;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s ease;
}

.new-chat:hover {
  background: rgba(56, 189, 248, 0.2);
}

.collapse-toggle {
  position: absolute;
  top: 12px;
  right: 6px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(15, 23, 42, 1);
  color: #e2e8f0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
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

.rail-avatar {
  margin-top: auto;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

  .rail-avatar .avatar {
    width: 44px;
    height: 44px;
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.35);
    background: rgba(37, 99, 235, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: #f8fafc;
  }

  .rail-avatar .avatar span {
    display: inline-flex;
    width: 100%;
    height: 100%;
    align-items: center;
    justify-content: center;
    color: #f8fafc;
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
  position: relative;
} 

.conversation-link {
  width: 100%;
  background: none;
  border: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  text-align: left;
  padding: 0;
  cursor: pointer;
}

.conversation-item:hover {
  border-color: rgba(59, 130, 246, 0.4);
  background: rgba(59, 130, 246, 0.12);
}

.conversation-delete {
  display: none;
  position: absolute;
  top: 6px;
  right: 10px;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.85);
  color: #e0e7ff;
  font-size: 12px;
  cursor: pointer;
}

.conversation-item:hover .conversation-delete {
  display: flex;
  align-items: center;
  justify-content: center;
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


.login-btn {
  border: none;
  border-radius: 14px;
  padding: 12px;
  background: linear-gradient(135deg, #22d3ee, #a855f7);
  color: #030712;
  font-weight: 600;
  cursor: pointer;
}

.login-btn:hover {
  opacity: 0.95;
}

.account-row {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: space-between;
}

.avatar-chip {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
}

.avatar-chip span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #fff;
  font-size: 16px;
}

.logout-btn {
  border: none;
  border-radius: 10px;
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.08);
  color: #e0e7ff;
  font-weight: 600;
  cursor: pointer;
  flex: 0 0 48%;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
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
  background: transparent;
  border-color: transparent;
  color: #f3f4f6;
  box-shadow: none;
  max-width: 100%;
  width: 100%;
  padding: 0;
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
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  position: sticky;
  bottom: 0;
  z-index: 2;
  flex-shrink: 0;
  background: rgba(32, 33, 35, 0.96);
}

.composer form {
  display: flex;
}

.composer-field {
  position: relative;
  width: 100%;
}

.composer textarea {
  width: 100%;
  min-height: 38px;
  max-height: calc(1.5rem * 5);
  height: 38px;
  resize: none;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(3, 7, 18, 0.6);
  color: #f8fafc;
  padding: 10px 16px 10px 16px;
  padding-right: 96px;
  font-size: 15px;
  line-height: 1.5;
  font-family: inherit;
  overflow-y: hidden;
  transition: border 0.2s ease;
}

.composer textarea:focus {
  outline: none;
  border-color: rgba(236, 72, 153, 0.6);
  box-shadow: 0 0 0 1px rgba(236, 72, 153, 0.15);
}

.composer textarea::-webkit-scrollbar {
  height: 6px;
}

.composer textarea::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.4);
}

.composer button {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  border: none;
  border-radius: 50%;
  background: transparent;
  color: #e2e8f0;
  font-size: 16px;
  padding: 6px 10px;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.composer button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.composer button:not(:disabled):hover {
  transform: translateY(-50%) scale(1.02);
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
