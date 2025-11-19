<template>
  <section class="class-card">
    <header class="card-head">
      <div>
        <p class="eyebrow">班级管理</p>
        <h3>班级与学生概览</h3>
        <small>点击卡片可锁定班级，底部展示完整学生列表</small>
      </div>
      <div class="metrics">
        <div class="metric">
          <p>班级</p>
          <strong>{{ payload.classes.length }}</strong>
        </div>
        <div class="metric">
          <p>学生</p>
          <strong>{{ totalStudents }}</strong>
        </div>
        <div class="metric accent">
          <p>平均人数</p>
          <strong>{{ averageStudents }}</strong>
        </div>
      </div>
    </header>

    <div class="class-grid">
      <article
        v-for="cls in payload.classes"
        :key="cls.id"
        :class="['class-panel', { active: cls.id === selectedClass }]"
        @click="selectClass(cls.id)"
      >
        <header>
          <span class="class-tag">班级 #{{ cls.id }}</span>
          <button type="button" class="ghost-btn">
            {{ cls.id === selectedClass ? '正在查看' : '查看' }}
          </button>
        </header>
        <h4>{{ cls.name }}</h4>
        <p class="class-meta">
          {{ getStudents(cls.id).length }} 名学生 · 占比 {{ progress(cls.id) }}%
        </p>
        <div class="chip-row">
          <span
            v-for="stu in getStudents(cls.id).slice(0, 3)"
            :key="stu.id"
            class="chip"
          >
            {{ stu.name }}
          </span>
          <span
            v-if="getStudents(cls.id).length > 3"
            class="chip more"
          >
            +{{ getStudents(cls.id).length - 3 }}
          </span>
          <span v-if="!getStudents(cls.id).length" class="chip empty">暂无学生</span>
        </div>
        <div class="progress-track">
          <div class="progress-bar" :style="{ width: `${progress(cls.id)}%` }"></div>
        </div>
      </article>
    </div>

    <section class="roster-panel">
      <template v-if="currentClass">
        <header class="roster-head">
          <div>
            <p class="eyebrow">学生列表</p>
            <h4>{{ currentClass.name }}</h4>
          </div>
          <span class="badge">{{ currentStudents.length }} 人</span>
        </header>
        <div class="roster-grid" v-if="currentStudents.length">
          <article
            v-for="stu in currentStudents"
            :key="stu.id"
            class="student-card"
          >
            <div class="avatar">{{ stu.name.slice(0, 1) }}</div>
            <div>
              <strong>{{ stu.name }}</strong>
              <small>ID {{ stu.id }}</small>
            </div>
          </article>
        </div>
        <div v-else class="empty-state">
          暂无学生，可在后台新增
        </div>
      </template>
      <div v-else class="empty-state">
        请选择上方某个班级以查看学生名单
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  payload: {
    type: Object,
    required: true
  }
});

const selectedClass = ref(props.payload.classes[0]?.id ?? null);

const currentClass = computed(() =>
  props.payload.classes.find((c) => c.id === selectedClass.value)
);

const currentStudents = computed(() => getStudents(selectedClass.value));

const totalStudents = computed(() =>
  Object.values(props.payload.students || {}).reduce(
    (acc, list) => acc + list.length,
    0
  )
);

const averageStudents = computed(() => {
  if (!props.payload.classes.length) return 0;
  return Math.round(totalStudents.value / props.payload.classes.length);
});

function getStudents(classId) {
  if (!classId) return [];
  return props.payload.students[classId] || [];
}

function selectClass(id) {
  selectedClass.value = id;
}

function progress(classId) {
  const count = getStudents(classId).length;
  if (!totalStudents.value) return 0;
  return Math.round((count / totalStudents.value) * 100);
}
</script>

<style scoped>
.class-card {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 22px;
  border: 1px solid #e2e8f0;
  border-radius: 24px;
  background: #fff;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.08em;
  color: #94a3b8;
  text-transform: uppercase;
}

.card-head h3 {
  margin: 6px 0 4px;
}

.metrics {
  display: flex;
  gap: 10px;
}

.metric {
  width: 90px;
  padding: 10px;
  border-radius: 14px;
  border: 1px solid #e0e7ff;
  background: #f8fafc;
  text-align: center;
}

.metric.accent {
  border-color: #fed7aa;
  background: #fff7ed;
}

.metric p {
  margin: 0;
  font-size: 12px;
  color: #475569;
}

.metric strong {
  display: block;
  margin-top: 4px;
  font-size: 20px;
  color: #0f172a;
}

.class-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
}

.class-panel {
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 16px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 12px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}

.class-panel.active {
  border-color: #2563eb;
  background: #eef2ff;
  box-shadow: 0 18px 40px rgba(37, 99, 235, 0.18);
}

.class-panel header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #475569;
}

.class-tag {
  font-weight: 600;
  color: #1d4ed8;
}

.ghost-btn {
  border: none;
  background: transparent;
  color: #475569;
  font-size: 12px;
  cursor: pointer;
}

.class-panel h4 {
  margin: 0;
  font-size: 16px;
}

.class-meta {
  margin: 0;
  color: #475569;
  font-size: 13px;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  padding: 4px 10px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 12px;
}

.chip.more {
  background: #fee2e2;
  color: #b91c1c;
}

.chip.empty {
  background: #e2e8f0;
  color: #475569;
}

.progress-track {
  height: 6px;
  border-radius: 999px;
  background: #e2e8f0;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(135deg, #2563eb, #9333ea);
}

.roster-panel {
  border: 1px dashed #cbd5f5;
  border-radius: 20px;
  padding: 20px;
  background: #fff;
  min-height: 220px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.roster-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.roster-head h4 {
  margin: 4px 0 0;
}

.badge {
  padding: 5px 12px;
  border-radius: 999px;
  background: #2563eb;
  color: #fff;
  font-size: 13px;
}

.roster-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 10px;
}

.student-card {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f8fafc;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: #c7d2fe;
  color: #312e81;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 28px;
  border-radius: 16px;
  border: 1px dashed #e2e8f0;
  color: #94a3b8;
}

@media (max-width: 900px) {
  .card-head {
    flex-direction: column;
  }

  .metrics {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
