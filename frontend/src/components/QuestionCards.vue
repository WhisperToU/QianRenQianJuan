<template>
  <section class="question-grid">
    <article v-for="item in entries" :key="item.id" class="question-card">
      <header class="card-head">
        <div>
          <p class="tile-id">Q{{ String(item.id).padStart(3, '0') }}</p>
          <h4>{{ item.title }}</h4>
        </div>
        <span class="status-chip">{{ item.status || '草稿' }}</span>
      </header>

      <div class="meta-row">
        <span class="topic-chip">{{ item.topic }}</span>
        <span class="difficulty-chip" :data-level="item.difficulty">
          难度 · {{ difficultyLabel[item.difficulty] || item.difficulty }}
        </span>
      </div>

      <div class="text-stack">
        <label>
          <span>题干</span>
          <p>{{ item.question }}</p>
        </label>
        <label>
          <span>答案/解析</span>
          <p>{{ item.answer }}</p>
        </label>
      </div>

      <footer class="card-foot">
        <small>题型：{{ item.type || '主观题' }} · 预计用时 {{ item.duration || '5' }} 分钟</small>
      </footer>
    </article>
  </section>
</template>

<script setup>
const props = defineProps({
  payload: {
    type: Object,
    required: true
  }
});

const entries = props.payload.questions || [];

const difficultyLabel = {
  easy: '基础',
  medium: '进阶',
  hard: '挑战'
};
</script>

<style scoped>
.question-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  width: 100%;
}

.question-card {
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 18px;
  padding: 16px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
}

.card-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.tile-id {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
}

.card-head h4 {
  margin: 4px 0 0;
  font-size: 16px;
  color: #0f172a;
}

.status-chip {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  background: #eff6ff;
  color: #1d4ed8;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 13px;
}

.topic-chip {
  padding: 4px 10px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
}

.difficulty-chip {
  padding: 4px 10px;
  border-radius: 999px;
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

.text-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.text-stack label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: #475569;
}

.text-stack p {
  margin: 0;
  background: #f8fafc;
  border-radius: 12px;
  padding: 10px 12px;
  min-height: 80px;
  color: #0f172a;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-foot {
  margin-top: auto;
  color: #94a3b8;
  font-size: 12px;
}
</style>
