<template>
  <section class="question-grid">
    <article
      v-for="card in cards"
      :key="card.uid"
      :class="['question-card', { saved: card.saved }]"
    >
      <header class="card-head">
        <div>
          <h4 v-if="!card.editing">{{ card.title }}</h4>
          <input
            v-else
            v-model="card.title"
            class="title-input"
            type="text"
            placeholder="请输入题目名称"
          />
        </div>
        <span v-if="card.saved" class="badge">已入库</span>
      </header>

      <div class="meta-grid">
        <div class="field">
          <template v-if="card.editing">
            <select
              v-if="topicOptions.length"
              :value="card.topic_id ?? ''"
              @change="handleTopicSelection(card, $event)"
            >
              <option value="" disabled hidden>请选择专题</option>
              <option
                v-for="option in topicOptions"
                :key="option.id"
                :value="option.id"
              >
                {{ option.name }}
              </option>
            </select>
            <input
              v-else
              v-model="card.topic"
              type="text"
              placeholder="例：函数与图像"
            />
          </template>
          <span v-else class="topic-pill">
            {{ card.topic || '未命名专题' }}
          </span>
        </div>
        <div class="field">
          <select v-if="card.editing" v-model="card.difficulty">
            <option
              v-for="option in difficultyOptions"
              :key="option"
              :value="option"
            >
              {{ difficultyLabel[option] }}
            </option>
          </select>
          <span
            v-else
            class="difficulty-pill"
            :data-level="card.difficulty"
          >
            {{ difficultyLabel[card.difficulty] || card.difficulty }}
          </span>
        </div>
      </div>
      <div class="qa-grid">
        <div class="qa-block">
          <p class="qa-label">题干</p>
          <textarea
            v-if="card.editing"
            v-model="card.question"
            class="qa-input"
            rows="4"
          ></textarea>
          <p v-else class="qa-text">{{ card.question }}</p>
          <label v-if="card.editing" class="field image-field">
            <span>题图链接（可选）</span>
            <input
              v-model="card.imageUrl"
              type="text"
              placeholder="https://example.com/diagram.png"
            />
          </label>
          <div v-if="card.imageUrl" class="question-image-preview">
            <img :src="card.imageUrl" alt="题图预览" />
          </div>
        </div>
        <div class="qa-block">
          <p class="qa-label">答/解析</p>
          <textarea
            v-if="card.editing"
            v-model="card.answer"
            class="qa-input"
            rows="4"
          ></textarea>
          <p v-else class="qa-text">{{ card.answer }}</p>
        </div>
      </div>

      <div class="card-actions">
        <button type="button" class="ghost-btn" @click="toggleEdit(card)">
          {{ card.editing ? '取消编辑' : '编辑' }}
        </button>
        <button
          type="button"
          class="primary-btn"
          :disabled="!card.editing || card.saving"
          @click="saveCard(card)"
        >
          {{ card.saving ? '保存中...' : '保存' }}
        </button>
      </div>
      <p v-if="card.errorMsg" class="error-tip">{{ card.errorMsg }}</p>
    </article>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue';

const props = defineProps({
  payload: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['save']);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const difficultyLabel = {
  easy: 'easy',
  medium: 'medium',
  difficult: 'difficult'
};

const difficultyOptions = Object.keys(difficultyLabel);

const cards = ref(createCards(props.payload.questions));
const topicOptions = computed(() => {
  const raw = props.payload?.topicOptions;
  if (!Array.isArray(raw)) return [];
  return raw
    .map((item) => {
      if (!item) return null;
      if (typeof item === 'string') {
        return { id: item, name: item };
      }
      return {
        id: item.id ?? item.name ?? '',
        name: item.name ?? String(item.id ?? '')
      };
    })
    .filter((option) => option && option.name);
});

function normalizeDifficulty(value) {
  const normalized = String(value || '')
    .toLowerCase()
    .trim();
  if (normalized === 'easy') return 'easy';
  if (normalized === 'medium') return 'medium';
  if (normalized === 'hard' || normalized === 'difficult') return 'difficult';
  return 'medium';
}

watch(
  () => props.payload.questions,
  (next) => {
    cards.value = createCards(next);
  },
  { deep: true }
);

function createCards(list = []) {
  return (list || []).map((item, idx) => ({
    uid: item.uid ?? item.id ?? item.question_id ?? `temp-${idx + 1}`,
    id: item.question_id ?? null,
    title: item.title ?? `题目 ${idx + 1}`,
    topic: item.topic ?? '',
    topic_id: item.topic_id ?? item.topicId ?? null,
    difficulty: normalizeDifficulty(item.difficulty ?? item.difficulty_level ?? 'medium'),
    question: item.question ?? '',
    answer: item.answer ?? '',
    type: item.type,
    duration: item.duration,
    imageUrl: item.question_image ?? item.imageUrl ?? '',
    editing: false,
    persisted: item.persisted ?? Boolean(item.question_id),
    saved: Boolean(item.saved ?? (item.persisted ?? Boolean(item.question_id))),
    saving: false,
    errorMsg: ''
  }));
}

function toggleEdit(card) {
  card.editing = !card.editing;
  if (card.editing) {
    card.saved = false;
    card.errorMsg = '';
  } else if (card.id) {
    card.saved = true;
  }
}

function handleTopicSelection(card, event) {
  const value = event.target.value;
  const option = topicOptions.value.find((item) => String(item.id) === value);
  if (option) {
    card.topic = option.name;
    card.topic_id = option.id;
  } else {
    card.topic_id = null;
  }
}

async function saveCard(card) {
  if (!card.editing || card.saving) return;

  const payload = {
    title: card.title,
    topic: card.topic,
    topic_id: card.topic_id,
    difficulty_level: normalizeDifficulty(card.difficulty),
    question_text: card.question,
    answer_text: card.answer,
    question_image: card.imageUrl,
    type: card.type,
    duration: card.duration
  };

  const isUpdate = Boolean(card.id);
  const url = isUpdate
    ? `${API_BASE_URL}/questions/${card.id}`
    : `${API_BASE_URL}/questions`;

  card.saving = true;
  card.errorMsg = '';

  try {
    const response = await fetch(url, {
      method: isUpdate ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error || '保存失败，请稍后重试');
    }

    const persistedId = data.question_id ?? data.id;
    if (persistedId) {
      card.id = persistedId;
    }

    card.saved = true;
    card.editing = false;
    emit('save', { ...payload, id: card.id });
  } catch (error) {
    card.errorMsg = error?.message || '保存失败，请稍后重试';
  } finally {
    card.saving = false;
  }
}
</script>

<style scoped>
.question-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  width: 100%;
}

.question-card {
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 16px;
  padding: 16px 14px 14px;
  background: rgba(8, 12, 20, 0.95);
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 12px 28px rgba(2, 6, 23, 0.45);
  transition: border-color 0.2s ease, background 0.2s ease, color 0.2s ease;
}

.question-card.saved {
  border-color: rgba(71, 85, 105, 0.35);
  background: rgba(6, 9, 15, 0.92);
  color: rgba(148, 163, 184, 0.65);
}

.card-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.card-head h4 {
  margin: 0;
  font-size: 16px;
  color: #f8fafc;
}

.title-input {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  padding: 6px 10px;
  background: rgba(15, 23, 42, 0.8);
  color: #f8fafc;
}

.badge {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(100, 116, 139, 0.18);
  color: rgba(226, 232, 240, 0.85);
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  font-size: 13px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field input,
.field select {
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(15, 23, 42, 0.8);
  color: #f8fafc;
  padding: 8px 10px;
  font-size: 13px;
}

.field select {
  text-transform: capitalize;
}

.image-field input {
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(15, 23, 42, 0.85);
  color: #f8fafc;
  padding: 8px 10px;
  font-size: 13px;
}

.question-image-preview img {
  width: 100%;
  max-height: 180px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  object-fit: cover;
  margin-top: 6px;
}

.topic-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(14, 165, 233, 0.2);
  color: #7dd3fc;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.question-card.saved .topic-pill {
  background: rgba(51, 65, 85, 0.45);
  color: rgba(226, 232, 240, 0.85);
  font-weight: 500;
}

.difficulty-pill {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(51, 65, 85, 0.7);
  color: #e2e8f0;
}

.difficulty-pill[data-level='easy'] {
  background: rgba(34, 197, 94, 0.18);
  color: #4ade80;
}

.difficulty-pill[data-level='medium'] {
  background: rgba(249, 115, 22, 0.18);
  color: #fb923c;
}

.difficulty-pill[data-level='difficult'] {
  background: rgba(248, 113, 113, 0.18);
  color: #fca5a5;
}

.question-card.saved .difficulty-pill {
  background: rgba(51, 65, 85, 0.6);
  color: rgba(226, 232, 240, 0.9);
}

.qa-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}

.qa-block {
  border-radius: 12px;
  padding: 10px 12px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(2, 6, 23, 0.65);
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 96px;
}

.qa-label {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(148, 163, 184, 0.85);
}

.qa-text {
  margin: 0;
  color: #f1f5f9;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.qa-input {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.85);
  color: #f8fafc;
  padding: 8px 10px;
  font-size: 13px;
  line-height: 1.4;
  resize: vertical;
}

.card-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.ghost-btn,
.primary-btn {
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 8px 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.ghost-btn {
  background: transparent;
  border-color: rgba(148, 163, 184, 0.4);
  color: #e2e8f0;
}

.primary-btn {
  border: none;
  background: linear-gradient(135deg, #22d3ee, #a855f7);
  color: #0f172a;
}

.primary-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.ghost-btn:hover,
.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.question-card.saved {
  background: rgba(7, 9, 14, 0.92);
  color: rgba(148, 163, 184, 0.6);
}

.question-card.saved :is(.badge, .topic-pill, .difficulty-pill, .qa-label, .ghost-btn, .primary-btn, h4) {
  color: inherit;
  border-color: rgba(71, 85, 105, 0.3);
  background: rgba(34, 40, 54, 0.35);
}

.question-card.saved .ghost-btn,
.question-card.saved .primary-btn {
  opacity: 0.6;
}

.question-card.saved .qa-text {
  color: rgba(226, 232, 240, 0.78);
  font-weight: 600;
}

.error-tip {
  margin: 6px 0 0;
  font-size: 12px;
  color: #f87171;
  text-align: right;
}
</style>
