<template>
  <div class="card">
    <header>
      <h3>原题录入</h3>
    </header>
    <form @submit.prevent>
      <div class="section">
        <div class="inline-grid">
          <div class="field-row">
            <label class="sr-only">考试类型</label>
            <select v-model="form.exam_type" :title="'考试类型'">
              <option disabled value="">考试类型</option>
              <option v-for="opt in examTypes" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div class="field-row">
            <label class="sr-only">考试年份</label>
            <input type="number" v-model="form.exam_year" placeholder="考试年份" :title="'考试年份'" />
          </div>
          <div class="field-row">
            <label class="sr-only">地区</label>
            <input type="text" v-model="form.exam_region" placeholder="地区" :title="'地区'" />
          </div>
        </div>
      </div>

      <div class="section">
        <div class="field-row inline-row">
          <label>题号</label>
          <input class="narrow" type="text" v-model="form.question_no" placeholder="12" />
        </div>
        <div class="field-row">
          <label>题干</label>
          <textarea v-model="form.question_stem" rows="4" placeholder="已知函数 f(x)..."></textarea>
        </div>
        <div class="field-row">
          <label>参考答案</label>
          <textarea v-model="form.answer" rows="3" placeholder="答案或解析"></textarea>
        </div>
      </div>

      <div class="actions">
        <button type="button" @click="reset">重置示例</button>
        <button type="button" class="primary">模拟保存</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const props = defineProps({
  payload: {
    type: Object,
    required: true
  }
})

const defaults = props.payload?.defaults || {}
const examTypes = [
  { label: '月考', value: 'monthly' },
  { label: '期中', value: 'midterm' },
  { label: '期末', value: 'final' },
  { label: '高考', value: 'gaokao' },
  { label: '模拟', value: 'mock' },
  { label: '其他', value: 'other' }
]

const form = reactive({
  exam_type: defaults.exam_type || '',
  exam_year: defaults.exam_year || '',
  exam_region: defaults.exam_region || '',
  question_no: defaults.question_no || '',
  question_stem: defaults.question_stem || '',
  answer: defaults.answer || ''
})

function reset() {
  form.exam_type = defaults.exam_type || ''
  form.exam_year = defaults.exam_year || ''
  form.exam_region = defaults.exam_region || ''
  form.question_no = defaults.question_no || ''
  form.question_stem = defaults.question_stem || ''
  form.answer = defaults.answer || ''
}
</script>

<style scoped>
.card {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.03);
  color: #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: min(480px, 100%);
  max-width: 100%;
}
header h3 {
  margin: 0;
  font-size: 16px;
}
.section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px 0;
}
.section + .section {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  margin-top: 8px;
  padding-top: 14px;
}
.field-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.inline-row {
  flex-direction: row;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}
.inline-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(110px, 1fr));
  gap: 8px;
}
label {
  font-size: 13px;
  color: #cbd5e1;
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
input,
select,
textarea {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 8px 10px;
  color: #e5e7eb;
  font-size: 14px;
}
textarea {
  resize: vertical;
}
.narrow {
  width: 120px;
  max-width: 100%;
}
.actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 4px;
}
button {
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: #e5e7eb;
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
}
button.primary {
  background: linear-gradient(135deg, #22d3ee, #a855f7);
  color: #0f172a;
  border: none;
}
</style>
