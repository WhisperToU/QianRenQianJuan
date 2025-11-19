<template>
  <div class="card assign-card">
    <div>
      <h3 style="margin:0 0 6px">分配题目</h3>
      <small>模拟 POST /assign/one</small>
    </div>
    <label>班级</label>
    <select v-model="selectedClass">
      <option
        v-for="cls in payload.classes"
        :key="cls.id"
        :value="cls.id"
      >
        {{ cls.name }}
      </option>
    </select>
    <label>学生（多选）</label>
    <div class="student-list">
      <label v-for="stu in studentOptions" :key="stu.id" style="display:block;font-size:13px">
        <input
          type="checkbox"
          :value="stu.id"
          v-model="selectedStudents"
        />
        {{ stu.name }}
      </label>
      <span v-if="!studentOptions.length" style="font-size:13px;color:#94a3b8">暂无学生</span>
    </div>
    <label>专题</label>
    <select v-model="selectedTopic">
      <option v-for="topic in payload.topics" :key="topic" :value="topic">
        {{ topic }}
      </option>
    </select>
    <label>难度</label>
    <select v-model="selectedDifficulty">
      <option value="easy">easy</option>
      <option value="medium">medium</option>
      <option value="hard">hard</option>
    </select>
    <button class="btn-primary" @click="assign">生成任务</button>
    <div v-if="log" class="log">{{ log }}</div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';

const props = defineProps({
  payload: {
    type: Object,
    required: true
  }
});

const selectedClass = ref(props.payload.classes[0]?.id ?? null);
const selectedStudents = ref([]);
const selectedTopic = ref(props.payload.topics[0] ?? '');
const selectedDifficulty = ref('medium');
const log = ref('');

const studentOptions = computed(() => props.payload.students[selectedClass.value] || []);

watch(selectedClass, () => {
  selectedStudents.value = [];
});

function assign() {
  if (!selectedStudents.value.length) {
    alert('请至少选择一个学生');
    return;
  }
  const payload = {
    student_ids: selectedStudents.value,
    topic: selectedTopic.value,
    difficulty_level: selectedDifficulty.value
  };
  log.value = `POST /assign/one\n${JSON.stringify(payload, null, 2)}\n✅ 分配成功（mock）`;
}
</script>

<style scoped>
.student-list {
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 8px;
}
</style>
