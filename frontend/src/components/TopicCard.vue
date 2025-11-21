<template>
  <div class="card">
    <header>
      <h3>专题</h3>
    </header>
    <form @submit.prevent>
      <div class="inline-grid trio">
        <div class="field-row">
          <input type="text" v-model="form.name" placeholder="专题名称" :title="'专题名称'" />
        </div>
        <div class="field-row">
          <input class="short" type="number" v-model="form.source_id" placeholder="所属母题编号" :title="'所属母题编号'" />
        </div>
        <div class="field-row">
          <input type="text" v-model="form.author_name" placeholder="作者" :title="'作者'" />
        </div>
      </div>
      <div class="divider"></div>
      <div class="field-row">
        <label>适合的学生群体说明</label>
        <textarea v-model="form.student_description" rows="3" placeholder="针对高一学生的函数基础"></textarea>
      </div>
      <div class="field-row">
        <label>容易——设计说明</label>
        <textarea v-model="form.easy_description" rows="2" placeholder="定义域、值域基础练习"></textarea>
      </div>
      <div class="field-row">
        <label>中等——设计说明</label>
        <textarea v-model="form.medium_description" rows="2" placeholder="单调性、奇偶性提升题"></textarea>
      </div>
      <div class="field-row">
        <label>复杂——设计说明</label>
        <textarea v-model="form.difficult_description" rows="2" placeholder="导数结合函数性质综合题"></textarea>
      </div>
      <div class="actions">
        <button type="button" @click="reset">重置示例</button>
        <button type="button" class="primary">模拟保存</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive } from 'vue';

const props = defineProps({
  payload: {
    type: Object,
    required: true
  }
});

const defaults = props.payload?.defaults || {};
const form = reactive({
  name: defaults.name || '',
  source_id: defaults.source_id || '',
  author_name: defaults.author_name || '',
  student_description: defaults.student_description || '',
  easy_description: defaults.easy_description || '',
  medium_description: defaults.medium_description || '',
  difficult_description: defaults.difficult_description || ''
});

function reset() {
  form.name = defaults.name || '';
  form.source_id = defaults.source_id || '';
  form.author_name = defaults.author_name || '';
  form.student_description = defaults.student_description || '';
  form.easy_description = defaults.easy_description || '';
  form.medium_description = defaults.medium_description || '';
  form.difficult_description = defaults.difficult_description || '';
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
.field-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.inline-grid.trio {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(0, 0.6fr) minmax(0, 1fr);
  gap: 6px;
}
.short {
  width: 100%;
  max-width: 100px;
}
label {
  font-size: 13px;
  color: #cbd5e1;
}
.divider {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  margin: 10px 0 16px;
}
input,
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
