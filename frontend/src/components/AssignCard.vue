<template>
  <section class="assign-card">
    <section class="section-card class-section bare">
      <ClassCard
        class="embedded-class-card"
        :payload="classCardPayload"
        selection-mode
        v-model="selectedStudents"
      />
    </section>
    <p v-if="dataError" class="error-text status-line">{{ dataError }}</p>
    <p v-else-if="classLoading" class="loading-text status-line">正在同步班级数据...</p>
    <p v-else-if="studentLoading" class="loading-text status-line">正在同步学生数据...</p>
    <p v-else-if="topicLoading" class="loading-text status-line">正在加载专题...</p>

    <section class="section-card topic-panel">
      <div class="section-head compact">
        <span v-if="selectedStudents.length" class="counter">
          已选 {{ selectedStudents.length }} 人
        </span>
        <span class="question-count">题库匹配：{{ questionCount }} 道</span>
      </div>

      <div class="topic-grid">
        <label class="field">
          <span>专题</span>
          <select v-model="selectedTopic">
            <option v-for="topic in topics" :key="topic" :value="topic">
              {{ topic }}
            </option>
            <option v-if="!topics.length" disabled>暂无专题</option>
          </select>
        </label>
        <div class="field">
          <span>难度</span>
          <div class="difficulty-tabs">
            <button
              v-for="option in difficultyOptions"
              :key="option.value"
              type="button"
              :class="['difficulty-btn', { active: selectedDifficulty === option.value }]"
              @click="selectedDifficulty = option.value"
            >
              {{ option.label }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="panel payload-panel">
      <div class="panel-head">
        <div>
          <p class="panel-kicker">请求体</p>
        </div>
        <button
          type="button"
          class="primary-btn"
          :disabled="!canAssign || isSubmitting || roundCompleted"
          @click="handleAssign"
        >
          {{ isSubmitting ? '提交中...' : '提交' }}
        </button>
      </div>
      <pre class="payload-json">{{ requestPreview }}</pre>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
      <p v-else-if="roundCompleted" class="round-info">本轮所有学生均已分配完成。</p>
      <p v-else-if="submissionMessage" class="success-text">{{ submissionMessage }}</p>
    </section>

    <section v-if="assignmentResult" class="panel result-panel">
      <div class="panel-head">
        <div>
          <p class="panel-kicker">分配结果</p>
          <h4>assigned</h4>
        </div>
        <span class="timestamp">{{ assignmentResult.timestamp }}</span>
      </div>
      <ul class="result-list">
        <li v-for="row in assignmentResult.entries" :key="row.student_id">
          <span class="student">{{ row.student_name }}</span>
          <span class="question">题号 #{{ row.question_id }}</span>
          <span class="position">位置 {{ row.position }}</span>
        </li>
      </ul>
      <pre class="payload-json">{{ assignmentResult.json }}</pre>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import ClassCard from './ClassCard.vue';

const props = defineProps({
  payload: {
    type: Object,
    required: true
  }
});

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const backendClasses = ref([]);
const backendStudents = ref({});
const backendTopics = ref([]);
const classLoading = ref(false);
const studentLoading = ref(false);
const topicLoading = ref(false);
const dataError = ref('');

const classes = computed(() =>
  backendClasses.value.length ? backendClasses.value : props.payload?.classes ?? []
);
const studentsMap = computed(() =>
  Object.keys(backendStudents.value).length ? backendStudents.value : props.payload?.students ?? {}
);
const topics = computed(() =>
  backendTopics.value.length ? backendTopics.value : props.payload?.topics ?? []
);

const availableStudents = ref(cloneStudents(studentsMap.value));

const selectedClass = ref(null);

const classCardPayload = computed(() => ({
  classes: classes.value,
  students: availableStudents.value
}));

const selectedStudents = ref([]);
const selectedTopic = ref(topics.value[0] ?? '');
const selectedDifficulty = ref('medium');
const assignmentResult = ref(null);
const errorText = ref('');
const submissionMessage = ref('');
const isSubmitting = ref(false);

const difficultyOptions = [
  { value: 'easy', label: 'easy' },
  { value: 'medium', label: 'medium' },
  { value: 'difficult', label: 'difficult' }
];

const difficultyMultiplier = {
  easy: 1.2,
  medium: 1,
  difficult: 0.6
};

const questionCount = computed(() => {
  if (!selectedTopic.value) return 0;
  const base = selectedTopic.value
    .split('')
    .reduce((sum, char) => sum + char.charCodeAt(0), 0);
  const normalized = (base % 35) + 5;
  const multiplier = difficultyMultiplier[selectedDifficulty.value] ?? 1;
  return Math.max(0, Math.round(normalized * multiplier));
});

const canAssign = computed(
  () => selectedStudents.value.length > 0 && Boolean(selectedTopic.value)
);

const remainingStudents = computed(() =>
  Object.values(availableStudents.value || {}).reduce((sum, list) => sum + (list?.length ?? 0), 0)
);

const roundCompleted = computed(() => remainingStudents.value === 0);

const requestPreview = computed(() =>
  JSON.stringify(
    {
      student_ids: selectedStudents.value,
      topic: selectedTopic.value || null,
      difficulty_level: selectedDifficulty.value
    },
    null,
    2
  )
);

watch(topics, (next) => {
  if (!next.length) {
    selectedTopic.value = '';
    return;
  }
  if (!next.includes(selectedTopic.value)) {
    selectedTopic.value = next[0];
  }
});

watch(
  () => props.payload,
  () => {
    availableStudents.value = cloneStudents(studentsMap.value);
    selectedStudents.value = [];
    assignmentResult.value = null;
  }
);

watch([selectedTopic, selectedDifficulty], () => {
  assignmentResult.value = null;
});

watch(
  selectedStudents,
  () => {
    assignmentResult.value = null;
  },
  { deep: true }
);

watch(
  studentsMap,
  (next) => {
    availableStudents.value = cloneStudents(next);
  },
  { deep: true }
);

watch(
  availableStudents,
  () => {
    const validIds = new Set(
      Object.values(availableStudents.value || {})
        .flat()
        .map((stu) => normalizeId(stu.id))
    );
    selectedStudents.value = selectedStudents.value.filter((id) => validIds.has(normalizeId(id)));
  },
  { deep: true }
);

watch(
  classes,
  (next) => {
    if (!hasAssignedClass() && next.length) {
      selectedClass.value = next[0]?.id ?? null;
    }
  },
  { immediate: true }
);

watch(selectedClass, (next) => {
  if (next) {
    ensureStudentsLoaded(next);
  }
});

onMounted(() => {
  fetchClasses();
  fetchTopics();
});

async function handleAssign() {
  if (!canAssign.value) {
    errorText.value = '请选择班级、学生和专题后再提交';
    return;
  }
  errorText.value = '';
  submissionMessage.value = '';
  assignmentResult.value = null;
  isSubmitting.value = true;

  const payload = {
    student_ids: [...selectedStudents.value],
    topic: selectedTopic.value,
    difficulty_level: selectedDifficulty.value
  };

  try {
    const response = await fetch(`${API_BASE_URL}/assign/one`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error || '分配失败，请稍后重试');
    }

    const entries = data.assigned || [];
    assignmentResult.value = {
      timestamp: new Date().toLocaleString('zh-CN', { hour12: false }),
      entries,
      json: JSON.stringify(data, null, 2)
    };
    removeAssignedStudents(payload.student_ids);
    submissionMessage.value = entries.length
      ? `已成功为 ${entries.length} 名学生分配题目。`
      : '已提交，未返回分配记录。';
    selectedStudents.value = [];
  } catch (error) {
    errorText.value = error?.message || '分配失败，请稍后重试';
  } finally {
    isSubmitting.value = false;
  }
}

function findStudentById(id) {
  const map = studentsMap.value || {};
  for (const list of Object.values(map)) {
    const target = list.find((stu) => stu.id === id);
    if (target) return target;
  }
  return null;
}

function removeAssignedStudents(ids = []) {
  if (!ids.length) return;
  const normalizedIds = new Set(ids.map((item) => normalizeId(item)).filter(Boolean));

  const updatedBackend = cloneStudents(backendStudents.value);
  Object.keys(updatedBackend).forEach((classId) => {
    updatedBackend[classId] = (updatedBackend[classId] || []).filter(
      (stu) => !normalizedIds.has(normalizeId(stu.id))
    );
  });
  backendStudents.value = updatedBackend;

  const updatedLocal = cloneStudents(availableStudents.value);
  Object.keys(updatedLocal).forEach((classId) => {
    updatedLocal[classId] = (updatedLocal[classId] || []).filter(
      (stu) => !normalizedIds.has(normalizeId(stu.id))
    );
  });
  availableStudents.value = updatedLocal;
}

function cloneStudents(source = {}) {
  const result = {};
  Object.entries(source || {}).forEach(([classId, list]) => {
    result[classId] = (list || []).map((stu) => ({ ...stu }));
  });
  return result;
}

function normalizeId(id) {
  if (id === null || id === undefined) return '';
  return String(id);
}

function hasAssignedClass() {
  return Boolean(selectedClass.value);
}

async function fetchClasses() {
  classLoading.value = true;
  dataError.value = '';
  try {
    const response = await fetch(`${API_BASE_URL}/classes/list`);
    const data = await response.json().catch(() => []);
    if (!response.ok) {
      throw new Error(data.error || '获取班级信息失败');
    }
    backendClasses.value = (data || []).map((item) => normalizeClass(item));
    if (!selectedClass.value && backendClasses.value.length) {
      selectedClass.value = backendClasses.value[0].id;
    }
  } catch (error) {
    dataError.value = error?.message || '获取班级信息失败';
  } finally {
    classLoading.value = false;
  }
}

async function fetchTopics() {
  topicLoading.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/questions/topics`);
    const data = await response.json().catch(() => []);
    if (!response.ok) {
      throw new Error(data.error || '获取专题失败');
    }
    backendTopics.value = (data || []).filter(Boolean);
    if (backendTopics.value.length && !selectedTopic.value) {
      selectedTopic.value = backendTopics.value[0];
    }
  } catch (error) {
    // keep fallback topics if api fails
  } finally {
    topicLoading.value = false;
  }
}

async function ensureStudentsLoaded(classId) {
  if (!classId) return;
  const existing = backendStudents.value[classId];
  if (existing && existing.length) return;
  await fetchStudentsForClass(classId);
}

async function fetchStudentsForClass(classId) {
  if (!classId) return;
  studentLoading.value = true;
  dataError.value = '';
  try {
    const response = await fetch(`${API_BASE_URL}/students/by_class?class_id=${classId}`);
    const data = await response.json().catch(() => []);
    if (!response.ok) {
      throw new Error(data.error || '获取学生信息失败');
    }
    backendStudents.value = {
      ...backendStudents.value,
      [classId]: (data || []).map((item) => normalizeStudent(item))
    };
  } catch (error) {
    dataError.value = error?.message || '获取学生信息失败';
  } finally {
    studentLoading.value = false;
  }
}

function normalizeClass(entry = {}) {
  return {
    id: entry.id ?? entry.class_id ?? entry.classId,
    name: entry.name ?? entry.class_name ?? entry.className ?? '未知班级'
  };
}

function normalizeStudent(entry = {}) {
  return {
    id: entry.id ?? entry.student_id ?? entry.studentId,
    name: entry.name ?? entry.student_name ?? entry.studentName ?? '未知学生'
  };
}

</script>

<style scoped>
.assign-card {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 24px;
  border-radius: 26px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(15, 23, 42, 0.92);
  color: #f8fafc;
  box-shadow: 0 24px 60px rgba(2, 6, 23, 0.45);
}

.section-card,
.panel {
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  padding: 18px;
  background: rgba(2, 6, 23, 0.75);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.section-card.bare {
  border: none;
  padding: 0;
  background: rgba(2, 6, 23, 0.75);
}

.class-section .embedded-class-card {
  margin: 0;
}
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.class-section .embedded-class-card {
  margin: 0;
}

.class-section :deep(.class-card) {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
}

.class-section :deep(.class-tabs) {
  background: transparent;
}

.section-head.compact {
  justify-content: flex-end;
}

.counter {
  border-radius: 999px;
  padding: 2px 10px;
  background: rgba(34, 197, 94, 0.18);
  color: #86efac;
  font-size: 12px;
}
.status-line {
  margin: 0;
  font-size: 12px;
  color: rgba(226, 232, 240, 0.75);
}
.loading-text {
  font-style: italic;
  color: rgba(203, 213, 225, 0.8);
}

.topic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: rgba(226, 232, 240, 0.85);
}

select {
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.85);
  color: #f8fafc;
  padding: 8px 10px;
}

.difficulty-tabs {
  display: flex;
  gap: 8px;
}

.difficulty-btn {
  flex: 1;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  padding: 8px 10px;
  background: rgba(15, 23, 42, 0.6);
  color: #e2e8f0;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 600;
}

.difficulty-btn.active {
  border-color: rgba(236, 72, 153, 0.7);
  color: #f472b6;
  background: rgba(236, 72, 153, 0.12);
}

.question-count {
  border-radius: 999px;
  padding: 4px 12px;
  background: rgba(14, 165, 233, 0.12);
  color: #7dd3fc;
  font-size: 12px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.panel-kicker {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.08em;
  color: rgba(148, 163, 184, 0.85);
  text-transform: uppercase;
}

.payload-json {
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.85);
  padding: 12px;
  font-size: 12px;
  white-space: pre-wrap;
  margin: 0;
  font-family: 'Fira Code', Consolas, monospace;
  color: #cbd5f5;
}

.primary-btn {
  border: none;
  border-radius: 12px;
  padding: 8px 16px;
  font-weight: 600;
  cursor: pointer;
  background: linear-gradient(135deg, #22d3ee, #a855f7);
  color: #0f172a;
}

.primary-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.result-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-list li {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
  font-size: 13px;
  border-radius: 12px;
  padding: 6px 10px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.timestamp {
  font-size: 12px;
  color: rgba(148, 163, 184, 0.8);
}

.error-text {
  margin: 0;
  color: #fca5a5;
  font-size: 13px;
}

.success-text,
.round-info {
  margin: 0;
  font-size: 13px;
  color: #86efac;
}

.round-info {
  color: rgba(148, 163, 184, 0.9);
}

@media (max-width: 640px) {
  .assign-card {
    padding: 18px;
  }

  .difficulty-tabs {
    flex-direction: column;
  }
}
</style>
