<template>
  <section class="overview-card">
    <header class="overview-head">
      <h3>题库结构概览</h3>
    </header>

    <div class="kpi-grid">
      <div class="kpi">
        <p class="kpi-label">专题总量</p>
        <p class="kpi-value">{{ payload.overview.totalTopics }}</p>
        <small>覆盖核心知识块</small>
      </div>
      <div class="kpi">
        <p class="kpi-label">题目总数</p>
        <p class="kpi-value">{{ payload.overview.totalQuestions }}</p>
        <small>含草稿与正式题</small>
      </div>
      <div class="kpi">
        <p class="kpi-label">涉及数据表</p>
        <p class="kpi-value">{{ payload.overview.tables.length }}</p>
        <small>questions / classes / …</small>
      </div>
    </div>

    <div class="topics-grid">
      <article
        v-for="topic in payload.overview.topics"
        :key="topic.name"
        class="topic-card"
      >
        <div class="topic-head">
          <div>
            <p class="topic-name">{{ topic.name }}</p>
            <small>{{ topic.count }} 题 · 难度分布如下</small>
          </div>
          <span class="topic-count">
            {{ Math.round((topic.count / payload.overview.totalQuestions) * 100) || 0 }}%
          </span>
        </div>
        <div class="difficulty-grid">
          <div
            v-for="[level, data] in difficultyEntries(topic.difficulties)"
            :key="level"
            class="difficulty-card"
            :data-level="level"
          >
            <p class="difficulty-title">
              {{ difficultyLabel[level] || level }}
              <span>· {{ data.count }} 题</span>
            </p>
            <small class="sample">例题：{{ data.sample }}</small>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  payload: {
    type: Object,
    required: true
  }
});

const difficultyLabel = {
  easy: '基础',
  medium: '进阶',
  hard: '挑战'
};

function difficultyEntries(difficulties) {
  if (!difficulties) return [];
  return Object.entries(difficulties);
}
</script>

<style scoped>
.overview-card {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 26px;
  background: radial-gradient(circle at 15% 20%, rgba(236, 72, 153, 0.12), transparent 60%),
    rgba(15, 23, 42, 0.92);
  color: #f1f5f9;
}

.overview-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.overview-head h3 {
  margin: 6px 0 0;
}

.badge {
  font-size: 12px;
  background: rgba(14, 165, 233, 0.2);
  color: #7dd3fc;
  padding: 4px 12px;
  border-radius: 999px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.kpi {
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 18px;
  padding: 16px;
  background: rgba(15, 23, 42, 0.8);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.kpi-label {
  margin: 0;
  font-size: 13px;
  color: rgba(226, 232, 240, 0.72);
}

.kpi-value {
  margin: 8px 0 4px;
  font-size: 28px;
  font-weight: 600;
  color: #f8fafc;
}

.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.topic-card {
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 20px;
  padding: 18px;
  background: rgba(15, 23, 42, 0.85);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.topic-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.topic-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.topic-count {
  font-size: 14px;
  color: #93c5fd;
  font-weight: 600;
}

.difficulty-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
}

.difficulty-card {
  border-radius: 16px;
  padding: 12px;
  background: rgba(30, 41, 59, 0.8);
  color: #e2e8f0;
}

.difficulty-card[data-level='easy'] {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
}

.difficulty-card[data-level='medium'] {
  background: rgba(249, 115, 22, 0.2);
  color: #fbbf24;
}

.difficulty-card[data-level='hard'] {
  background: rgba(248, 113, 113, 0.2);
  color: #fca5a5;
}

.difficulty-title {
  margin: 0 0 6px;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
}

.difficulty-title span {
  font-weight: 400;
}

.sample {
  color: inherit;
  opacity: 0.9;
}
</style>
