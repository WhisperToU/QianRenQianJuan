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

    <section class="section-card topic-panel">
      <div class="section-head compact">
        <span v-if="selectedStudents.length" class="counter">
          宸查€?{{ selectedStudents.length }} 浜?
        </span>
        <span class="question-count">棰樺簱鍖归厤锛歿{ questionCount }} 閬?/span>
      </div>

      <div class="topic-grid">
        <div class="topic-status">
          <p v-if="topicLoading" class="helper-text">Syncing topics...</p>
          <p v-else-if="topicError" class="error-text">{{ topicError }}</p>
        </div>
        <div class="assignment-grid">
          <article
            v-for="(row, rowIndex) in assignmentRows"
            :key="row.id"
            class="assignment-card"
          >
            <div class="assignment-card__header">
              <span class="assignment-card__index">涓撻 {{ rowIndex + 1 }}</span>
              <button
                v-if="assignmentRows.length > 1"
                type="button"
                class="icon-btn remove-row-btn"
                @click="removeAssignmentRow(row.id)"
              >
                鍒犻櫎
              </button>
            </div>
            <div class="assignment-card__body">
              <label class="field assignment-label">
                <span>涓撻</span>
                <select :value="row.topic" @change="handleTopicChange(row, $event.target.value)">
                  <option v-for="topic in topics" :key="topic" :value="topic">
                    {{ topic }}
                  </option>
                  <option v-if="!topics.length" disabled>鏆傛棤涓撻</option>
                </select>
              </label>
              <div class="field difficulty-field">
                <span>闅惧害</span>
                <div class="difficulty-tabs">
                  <button
                    v-for="option in difficultyOptions"
                    :key="option.value"
                    type="button"
                    :class="['difficulty-btn', { active: row.difficulty === option.value }]"
                    @click="handleDifficultyChange(row, option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>
              <p class="assignment-card__meta">
                <span v-if="row.countLoading">Querying database...</span>
                <span v-else-if="row.countError" class="error-text">{{ row.countError }}</span>
                <span v-else>题库数量：{{ row.availableCount ?? 'N/A' }}</span>
              </p>
            </div>
          </article>
          <button
            type="button"
            class="secondary-btn add-row-btn add-row-card"
            :disabled="roundCompleted"
            @click="addAssignmentRow"
          >
            + 娣诲姞棰樼洰
          </button>
        </div>
      </div>
    </section>

    <section class="panel payload-panel">
      <div class="panel-head">
        <div>
          <p class="panel-kicker">璇锋眰浣?/p>
        </div>
        <button
          type="button"
          class="primary-btn"
          :disabled="!canAssign || isSubmitting || roundCompleted"
          @click="handleAssign"
        >
          {{ isSubmitting ? '鎻愪氦涓?..' : '鎻愪氦' }}
        </button>
      </div>
      <pre class="payload-json">{{ requestPreview }}</pre>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
      <p v-else-if="roundCompleted" class="round-info">鏈疆鎵€鏈夊鐢熷潎宸插垎閰嶅畬鎴愩€?/p>
      <p v-else-if="submissionMessage" class="success-text">{{ submissionMessage }}</p>
    </section>

    <section v-if="assignmentResult" class="panel result-panel">
      <div class="panel-head">
        <div>
          <p class="panel-kicker">Mock Response</p>
          <h4>assigned</h4>
        </div>
        <span class="timestamp">{{ assignmentResult.timestamp }}</span>
      </div>
      <ul class="result-list">
        <li
          v-for="row in assignmentResult.entries"
          :key="`${row.student_id}-${row.question_id}`"
        >
          <span class="student">{{ row.student_name }}</span>
          <span class="question">棰樺彿 #{{ row.question_id }}</span>
          <span class="position">浣嶇疆 {{ row.position }}</span>
        </li>
      </ul>
      <pre class="payload-json">{{ assignmentResult.json }}</pre>
    </section>
  </section>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue';
import ClassCard from './ClassCard.vue';

const props = defineProps({
  payload: {
    type: Object,
    required: true
  }
});

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const classes = computed(() => props.payload?.classes ?? []);
const studentsMap = computed(() => props.payload?.students ?? {});
const topics = ref(props.payload?.topics ?? []);
const topicLoading = ref(false);
const topicError = ref('');

const availableStudents = ref(cloneStudents(studentsMap.value));

const classCardPayload = computed(() => ({
  classes: classes.value,
  students: availableStudents.value
}));

const selectedStudents = ref([]);
let assignmentRowId = 0;
const createAssignmentRow = (topic = topics.value[0] ?? '', difficulty = 'medium') => ({
  id: ++assignmentRowId,
  topic,
  difficulty,
  availableCount: null,
  countKey: '',
  countLoading: false,
  countError: ''
});
const assignmentRows = ref([createAssignmentRow()]);
const assignmentResult = ref(null);
const errorText = ref('');
const submissionMessage = ref('');
const isSubmitting = ref(false);

const difficultyOptions = [
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'difficult', label: 'Difficult' }
];

const questionCount = computed(() =>
  assignmentRows.value.reduce((total, row) => total + (row.availableCount ?? 0), 0)
);

const activeAssignments = computed(() =>
  assignmentRows.value
    .filter((row) => Boolean(row.topic))
    .map((row) => ({
      topic: row.topic,
      difficulty_level: row.difficulty
    }))
);

const canAssign = computed(
  () => selectedStudents.value.length > 0 && activeAssignments.value.length > 0
);

const remainingStudents = computed(() =>
  Object.values(availableStudents.value || {}).reduce((sum, list) => sum + (list?.length ?? 0), 0)
);

const roundCompleted = computed(() => remainingStudents.value === 0);

const requestPreview = computed(() =>
  JSON.stringify(
    {
      student_ids: selectedStudents.value,
      assignments: activeAssignments.value
    },
    null,
    2
  )
);

watch(
  topics,
  (next) => {
    assignmentRows.value.forEach((row) => {
      if (!next.length) {
        row.topic = '';
      } else if (!row.topic || !next.includes(row.topic)) {
        row.topic = next[0];
      }
      void refreshRowCount(row);
    });
  },
  { immediate: true }
);

watch(
  () => props.payload,
  (next) => {
    availableStudents.value = cloneStudents(studentsMap.value);
    selectedStudents.value = [];
    assignmentResult.value = null;
    const incomingTopics = next?.topics ?? [];
    if (!topics.value.length && Array.isArray(incomingTopics) && incomingTopics.length) {
      topics.value = incomingTopics;
    }
  }
);
watch(
  selectedStudents,
  () => {
    assignmentResult.value = null;
  },
  { deep: true }
);

watch(
  assignmentRows,
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

onMounted(() => {
  void loadTopics();
});

async function loadTopics() {
  topicLoading.value = true;
  topicError.value = '';
  try {
    const response = await fetch(`${API_BASE_URL}/questions/topics`);
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || 'Failed to load topics');
    }
    const data = await response.json();
    if (!Array.isArray(data)) {
      throw new Error('Topics format invalid');
    }
    topics.value = data;
  } catch (error) {
    topicError.value = error?.message ?? 'Failed to load topics';
  } finally {
    topicLoading.value = false;
  }
}

async function refreshRowCount(row) {
  const key = `${row.topic || ''}||${row.difficulty || ''}`;
  if (!row.topic || !row.difficulty) {
    row.availableCount = null;
    row.countKey = key;
    row.countError = '';
    row.countLoading = false;
    return;
  }
  if (row.countKey === key && !row.countLoading) {
    return;
  }
  row.countLoading = true;
  row.countError = '';
  const token = Symbol();
  row.fetchToken = token;
  try {
    const url = new URL(`${API_BASE_URL}/questions/count`);
    url.searchParams.set('topic', row.topic);
    url.searchParams.set('difficulty_level', row.difficulty);
    const response = await fetch(url);
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || 'Question pool query failed');
    }
    const data = await response.json();
    if (row.fetchToken !== token) return;
    row.availableCount = Number.isFinite(data?.count) ? data.count : 0;
    row.countKey = key;
  } catch (error) {
    if (row.fetchToken !== token) return;
    row.availableCount = 0;
    row.countError = error?.message ?? 'Question pool query failed';
  } finally {
    if (row.fetchToken === token) {
      row.countLoading = false;
    }
  }
}

function handleTopicChange(row, value) {
  if (row.topic === value) return;
  row.topic = value;
  row.countKey = '';
  row.availableCount = null;
  row.countError = '';
  void refreshRowCount(row);
}

function handleDifficultyChange(row, value) {
  if (row.difficulty === value) return;
  row.difficulty = value;
  row.countKey = '';
  row.availableCount = null;
  row.countError = '';
  void refreshRowCount(row);
}

async function handleAssign() {
  if (!canAssign.value) {
    errorText.value = '璇烽€夋嫨鐝骇銆佸鐢熷拰涓撻鍚庡啀鎻愪氦';
    return;
  }
  errorText.value = '';
  submissionMessage.value = '';
  assignmentResult.value = null;
  isSubmitting.value = true;

  const payload = {
    student_ids: [...selectedStudents.value],
    assignments: activeAssignments.value
  };

  setTimeout(() => {
    const entries = createMockAssignments(payload);
    const data = { assigned: entries };
    assignmentResult.value = {
      timestamp: new Date().toLocaleString('zh-CN', { hour12: false }),
      entries,
      json: JSON.stringify(data, null, 2)
    };
    removeAssignedStudents(payload.student_ids);
    submissionMessage.value = entries.length
      ? `宸叉垚鍔熶负 ${entries.length} 鍚嶅鐢熷垎閰嶉鐩€俙
      : '宸叉彁浜わ紝鏈繑鍥炲垎閰嶈褰曘€?;
    selectedStudents.value = [];
    isSubmitting.value = false;
  }, 500);
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
  const updated = cloneStudents(availableStudents.value);
  const normalizedIds = new Set(ids.map((item) => normalizeId(item)).filter(Boolean));
  Object.keys(updated).forEach((classId) => {
    updated[classId] = (updated[classId] || []).filter(
      (stu) => !normalizedIds.has(normalizeId(stu.id))
    );
  });
  availableStudents.value = updated;
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

function createMockAssignments(payload) {
  const rows = payload.assignments || [];
  const assignments = [];
  (payload.student_ids || []).forEach((stuId) => {
    rows.forEach((row, rowIndex) => {
      const base = row?.topic?.slice(0, 1) || 'Q';
      assignments.push({
        student_id: stuId,
        student_name: findStudentById(stuId)?.name ?? `ID ${stuId}`,
        question_id: `${base}${stuId}${rowIndex + 1}`,
        position: rowIndex + 1
      });
    });
  });
  return assignments;
}

function addAssignmentRow() {
  const row = createAssignmentRow(topics.value[0] ?? '', 'medium');
  assignmentRows.value.push(row);
  void refreshRowCount(row);
}

function removeAssignmentRow(id) {
  if (assignmentRows.value.length === 1) return;
  assignmentRows.value = assignmentRows.value.filter((row) => row.id !== id);
}

</script>

<style scoped>
.assign-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 18px;
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
  padding: 14px;
  background: rgba(2, 6, 23, 0.75);
  display: flex;
  flex-direction: column;
  gap: 10px;
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

.topic-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.topic-status {
  min-height: 20px;
}

.helper-text {
  margin: 0;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.75);
}

.assignment-card__meta {
  margin: 0;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.85);
}

.icon-btn {
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  padding: 4px 10px;
  color: #f87171;
  font-size: 13px;
  background: transparent;
  cursor: pointer;
}

.icon-btn:hover {
  border-color: rgba(248, 113, 113, 0.8);
  color: #fee2e2;
}

.assignment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, 260px);
  justify-content: center;
  gap: 10px;
}

.assignment-card {
  width: 260px;
  min-height: 210px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  padding: 12px;
  background: rgba(15, 23, 42, 0.8);
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 0 0 transparent;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.assignment-card:hover {
  border-color: rgba(14, 165, 233, 0.5);
  box-shadow: 0 8px 22px rgba(2, 6, 23, 0.35);
}

.assignment-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.assignment-card__index {
  font-size: 13px;
  letter-spacing: 0.05em;
  color: rgba(226, 232, 240, 0.6);
}

.assignment-card__body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.assignment-label select {
  min-width: 100%;
}

.remove-row-btn {
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.7);
  background: rgba(248, 113, 113, 0.12);
}

.remove-row-btn:hover {
  color: #fee2e2;
  background: rgba(248, 113, 113, 0.2);
}

.secondary-btn {
  align-self: flex-start;
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 12px;
  padding: 8px 18px;
  font-weight: 600;
  cursor: pointer;
  background: transparent;
  color: #bae6fd;
}

.secondary-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.add-row-btn {
  max-width: 220px;
}

.add-row-card {
  width: 260px;
  min-height: 210px;
  border-radius: 18px;
  border: 1px dashed rgba(59, 130, 246, 0.6);
  background: rgba(2, 6, 23, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  gap: 6px;
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
  width: 100%;
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


