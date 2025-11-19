<template>
  <section class="overview-card">
    <header class="overview-head">
      <div>
        <p class="eyebrow">数据快照 · mock</p>
        <h3>题库结构概览</h3>
      </div>
      <span class="badge">teaching_assistant</span>
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

    <div class="tables-block" v-if="payload.overview.tables?.length">
      <div class="block-head">
        <h4>关联数据表</h4>
        <small>{{ payload.overview.tables.length }} 张</small>
      </div>
      <div class="table-pills">
        <span
          v-for="table in payload.overview.tables"
          :key="table"
          class="pill"
        >
          {{ table }}
        </span>
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
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  background: #fff;
}

.overview-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.1em;
  color: #94a3b8;
  text-transform: uppercase;
}

.overview-head h3 {
  margin: 6px 0 0;
}

.badge {
  font-size: 12px;
  background: #e0f2fe;
  color: #0369a1;
  padding: 4px 10px;
  border-radius: 999px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.kpi {
  border: 1px solid #e0e7ff;
  border-radius: 16px;
  padding: 14px;
  background: #f8fafc;
}

.kpi-label {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

.kpi-value {
  margin: 8px 0 4px;
  font-size: 28px;
  font-weight: 600;
  color: #0f172a;
}

.tables-block {
  border: 1px dashed #cbd5f5;
  border-radius: 18px;
  padding: 16px;
}

.block-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.block-head h4 {
  margin: 0;
}

.table-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pill {
  padding: 5px 12px;
  border-radius: 999px;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 13px;
}

.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.topic-card {
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 16px;
  background: #fdfdfd;
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
  color: #2563eb;
  font-weight: 600;
}

.difficulty-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
}

.difficulty-card {
  border-radius: 14px;
  padding: 10px;
  background: #f1f5f9;
  color: #1f2937;
}

.difficulty-card[data-level='easy'] {
  background: #ecfccb;
  color: #3f6212;
}

.difficulty-card[data-level='medium'] {
  background: #fef3c7;
  color: #92400e;
}

.difficulty-card[data-level='hard'] {
  background: #fee2e2;
  color: #b91c1c;
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
