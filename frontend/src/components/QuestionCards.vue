<template>
  <section class="question-grid">
    <article
      v-for="item in entries"
      :key="item.id"
      class="question-tile"
      :class="{ saved: item.saved, editing: item.editing }"
    >
      <header class="tile-head">
        <div>
          <p class="tile-id">Q{{ String(item.id).padStart(3, '0') }}</p>
          <h4>{{ item.title }}</h4>
        </div>
        <span class="status-chip">
          {{ item.saved ? '已保存' : item.editing ? '编辑中' : '草稿' }}
        </span>
      </header>

      <div class="meta">
        <span class="topic-chip">{{ item.topic }}</span>
        <span class="difficulty-chip" :data-level="item.difficulty">
          难度 · {{ difficultyLabel[item.difficulty] || item.difficulty }}
        </span>
      </div>

      <div class="field-grid">
        <label class="field-block">
          <span>题干</span>
          <textarea
            v-model="item.question"
            rows="4"
            :disabled="!item.editing"
            placeholder="描述题目背景、给定条件与问题"
          />
        </label>
        <label class="field-block">
          <span>答案/解析</span>
          <textarea
            v-model="item.answer"
            rows="4"
            :disabled="!item.editing"
            placeholder="简述答案要点或讲解思路"
          />
        </label>
      </div>

      <footer class="tile-actions">
        <small class="hint">提示：先点击“编辑”即可批量调整题目内容</small>
        <div class="action-buttons">
          <button type="button" class="btn-ghost" @click="toggleEdit(item)">
            {{ item.editing ? '完成编辑' : '进入编辑' }}
          </button>
          <button type="button" class="btn-primary" @click="save(item)">
            保存
          </button>
        </div>
      </footer>

      <div v-if="item.log" class="log">
        {{ item.log }}
      </div>
    </article>
  </section>
</template>

<script setup>
import { reactive } from 'vue';

const props = defineProps({
  payload: {
    type: Object,
    required: true
  }
});

const entries = reactive(
  props.payload.questions.map((q) => ({
    ...q,
    editing: false,
    saved: false,
    log: ''
  }))
);

const difficultyLabel = {
  easy: '基础',
  medium: '进阶',
  hard: '挑战'
};

function toggleEdit(item) {
  item.editing = !item.editing;
}

function save(item) {
  item.saved = true;
  item.editing = false;
  const timestamp = new Date().toLocaleTimeString();
  item.log = `POST /questions (mock)\nquestion_id=Q${String(item.id).padStart(
    3,
    '0'
  )}\n保存时间：${timestamp}`;
}
</script>

<style scoped>
.question-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
  width: 100%;
}

.question-tile {
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 18px;
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: 14px;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}

.question-tile.editing {
  border-color: #f59e0b;
  box-shadow: 0 15px 30px rgba(245, 158, 11, 0.12);
}

.question-tile.saved {
  border-color: #34d399;
  background: #f0fdf4;
}

.tile-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.tile-id {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.08em;
  color: #94a3b8;
}

.tile-head h4 {
  margin: 4px 0 0;
  font-size: 17px;
}

.status-chip {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  background: #eff6ff;
  color: #1d4ed8;
}

.question-tile.saved .status-chip {
  background: #dcfce7;
  color: #15803d;
}

.question-tile.editing:not(.saved) .status-chip {
  background: #fef3c7;
  color: #b45309;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.topic-chip {
  padding: 4px 10px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 13px;
}

.difficulty-chip {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 13px;
  background: #e2e8f0;
  color: #475569;
}

.difficulty-chip[data-level='easy'] {
  background: #ecfccb;
  color: #3f6212;
}

.difficulty-chip[data-level='medium'] {
  background: #fef3c7;
  color: #b45309;
}

.difficulty-chip[data-level='hard'] {
  background: #fee2e2;
  color: #b91c1c;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.field-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  color: #475569;
}

.field-block textarea {
  border-radius: 14px;
  border: 1px solid #cbd5f5;
  padding: 10px 12px;
  resize: vertical;
  font-size: 14px;
  background: #f8fafc;
  min-height: 120px;
}

.field-block textarea:disabled {
  background: #f1f5f9;
  color: #94a3b8;
}

.tile-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hint {
  color: #94a3b8;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.btn-ghost,
.btn-primary {
  flex: 1;
  padding: 10px 0;
  border-radius: 12px;
  border: none;
  font-size: 14px;
  cursor: pointer;
}

.btn-ghost {
  background: #f1f5f9;
  color: #475569;
}

.btn-primary {
  background: #2563eb;
  color: #fff;
}

.log {
  font-size: 12px;
  background: #0f172a;
  color: #f8fafc;
  border-radius: 12px;
  padding: 10px 12px;
  white-space: pre-line;
}
</style>
