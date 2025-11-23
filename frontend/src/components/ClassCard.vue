<template>
  <section class="class-card">
    <div class="class-tabs" role="tablist" v-if="authed">
      <button
        v-for="cls in classList"
        :key="cls.id"
        type="button"
        :class="['tab-btn', { active: cls.id === selectedClass }]"
        @click="selectClass(cls.id)"
      >
        {{ cls.name }}
      </button>
      <button
        v-if="!selectionMode"
        type="button"
        class="tab-btn add-class-tab"
        :class="{ active: isAddMode }"
        @click="selectAddClass"
      >
        +
      </button>
    </div>

    <section class="tab-panel">
      <template v-if="!authed">
        <div class="empty-state">请登录后查看或导入班级与学生</div>
      </template>
      <template v-else>
      <template v-if="selectionMode">
        <template v-if="currentClass">
          <header class="roster-head selection-head">
            <span class="badge">{{ currentStudents.length }} 人</span>
            <span v-if="selectedCount" class="badge selected-badge">
              已选 {{ selectedCount }} 人
            </span>
          </header>

          <div class="roster-grid" v-if="currentStudents.length">
            <article
              v-for="stu in currentStudents"
              :key="stu.id"
              :class="['student-card', 'selectable-card', { selected: isStudentSelected(stu.id) }]"
              @click="toggleSelection(stu.id)"
            >
              <div class="avatar">{{ stu.name.slice(0, 1) }}</div>
              <div class="student-info">
                <strong>{{ stu.name }}</strong>
              </div>
              <span class="badge mini" v-if="isStudentSelected(stu.id)">已选</span>
            </article>
          </div>
          <div v-else class="empty-state">
            暂无学生，可在后台新增
          </div>
        </template>
        <div v-else class="empty-state">
          请选择上方某个班级以查看学生名单
        </div>
      </template>

      <template v-else-if="isAddMode">
        <div class="import-panel">
          <h4>添加新班级</h4>
          <p class="import-hint">
            请下载班级信息模板，填充后导入 Excel。字段可包含多列，但<strong>姓名</strong>列为必填项。
          </p>
          <div class="import-form">
            <div class="form-field">
              <label>班级名称</label>
              <input
                v-model="newClassName"
                type="text"
                class="inline-input class-name-input"
                placeholder="输入班级名称"
              />
            </div>
            <div class="form-field">
              <label>导入表格</label>
              <label class="upload-btn file-select">
                <input
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  @change="handleExcelUpload"
                  hidden
                />
                {{ excelFileName || '选择 Excel / CSV 文件' }}
              </label>
            </div>
          </div>
          <ol class="import-steps">
            <li>下载或复制 Excel 模板，填写班级与学生信息。</li>
            <li>确认每一行都包含学生姓名；其他列为可选。</li>
            <li>上传 Excel（支持 .xlsx / .xls / .csv），等待系统导入。</li>
          </ol>
          <button
            type="button"
            class="confirm-btn"
            :disabled="!canConfirmImport"
            @click="confirmImport"
          >
            确定导入
          </button>
          <p v-if="importError" class="error-text">{{ importError }}</p>
          <p v-else-if="importedStudents.length" class="import-preview">
            已识别 {{ importedStudents.length }} 名学生
          </p>
          <p class="import-note">导入完成后，新班级会自动生成并出现在选项卡列表中。</p>
        </div>
      </template>

      <template v-else>
        <template v-if="currentClass">
          <header class="roster-head">
            <span class="badge">{{ currentStudents.length }} 人</span>
          </header>

          <div class="roster-grid" v-if="currentStudents.length">
            <article
              v-for="stu in currentStudents"
              :key="stu.id"
              class="student-card"
            >
              <div class="avatar">{{ stu.name.slice(0, 1) }}</div>
              <div class="student-info">
                <strong>{{ stu.name }}</strong>
              </div>
              <button
                type="button"
                class="icon-btn remove-btn"
                @click.stop="removeStudent(stu.id)"
              >
                ×
              </button>
            </article>
            <article class="student-card add-card">
              <div class="avatar ghost">?</div>
              <div class="student-info">
                <input
                  ref="newStudentInput"
                  type="text"
                  v-model="newStudentName"
                  class="inline-input"
                  @keyup.enter.prevent="addStudent"
                />
              </div>
              <button
                type="button"
                class="icon-btn add-btn"
                @click.stop="handleAddButtonClick"
              >
                +
              </button>
            </article>
          </div>
          <div v-else class="empty-state">
            暂无学生，可在后台新增
          </div>
        </template>
        <div v-else class="empty-state">
          请选择上方某个班级以查看学生名单
        </div>
      </template>
      </template>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { apiFetch } from '../utils/api'

const ADD_CLASS_TAB = '__add_class__'

const emit = defineEmits(['importClass', 'update:modelValue', 'classChange'])

const props = defineProps({
  payload: {
    type: Object,
    default: () => ({ classes: [], students: {} })
  },
  selectionMode: {
    type: Boolean,
    default: false
  },
  modelValue: {
    type: Array,
    default: () => []
  }
})

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

const classList = ref([])
const selectedClass = ref(null)
const studentState = ref({})
const newStudentName = ref('')
const newStudentInput = ref(null)
const excelFileName = ref('')
const importedStudents = ref([])
const actionMessage = ref('')
const nextStudentId = ref(calcNextId(studentState.value))
const nextClassId = ref(calcNextClassId(classList.value))
const newClassName = ref('')
const importError = ref('')
const selectedStudentIds = ref(new Set(props.modelValue || []))
const hasSyncedClasses = ref(false)
const storedToken = ref(localStorage.getItem('auth_token') || '')

const hasToken = () => Boolean(storedToken.value)
const authed = computed(() => hasToken())

const canConfirmImport = computed(() =>
  Boolean(newClassName.value.trim()) && importedStudents.value.length > 0
)

const clearLocalState = () => {
  classList.value = []
  studentState.value = {}
  selectedClass.value = null
  newClassName.value = ''
  importedStudents.value = []
  excelFileName.value = ''
  actionMessage.value = ''
}

// -----------------------------------------------------
// Token 同步
// -----------------------------------------------------
function syncToken() {
  storedToken.value = localStorage.getItem('auth_token') || ''
  if (!storedToken.value) {
    clearLocalState()
  }
}
window.addEventListener('storage', syncToken)

const selectedCount = computed(() => selectedStudentIds.value.size)
const totalStudents = computed(() =>
  Object.values(studentState.value).reduce((sum, list) => sum + list.length, 0)
)
const averageStudents = computed(() =>
  classList.value.length ? Math.round(totalStudents.value / classList.value.length) : 0
)

const isAddMode = computed(() => !props.selectionMode && selectedClass.value === ADD_CLASS_TAB)

const currentClass = computed(() =>
  isAddMode.value ? null : classList.value.find((c) => c.id === selectedClass.value)
)

const currentStudents = computed(() => {
  if (isAddMode.value) return []
  if (props.selectionMode) {
    return props.payload?.students?.[selectedClass.value] || []
  }
  return getStudents(selectedClass.value)
})

watch(
  () => props.payload.classes,
  (next) => {
    if (!hasToken()) {
      clearLocalState()
      return
    }
    if (!props.selectionMode || !next) return
    classList.value = cloneClasses(next)
    nextClassId.value = calcNextClassId(classList.value)
    if (!classList.value.length) {
      selectedClass.value = null
      return
    }
    const already = classList.value.some((cls) => cls.id === selectedClass.value)
    if (!selectedClass.value || !already) {
      selectedClass.value = classList.value[0].id
    }
  },
  { deep: true, immediate: true }
)

watch(
  () => props.payload.students,
  (next) => {
    if (!hasToken()) {
      clearLocalState()
      return
    }
    if (!props.selectionMode || !next) return
    studentState.value = cloneStudents(next)
    nextStudentId.value = calcNextId(studentState.value)
  },
  { deep: true, immediate: true }
)

watch(selectedClass, (next) => {
  newStudentName.value = ''
  actionMessage.value = ''
  excelFileName.value = ''
  importedStudents.value = []
  importError.value = ''
  newClassName.value = ''
  if (!isAddMode.value && !props.selectionMode && next) {
    focusAddInput()
    ensureStudentsLoaded(next)
  }
})

watch(
  () => props.modelValue,
  (n) => {
    selectedStudentIds.value = new Set(n || [])
  },
  { deep: true }
)

watch(
  classList,
  (next) => {
    if (!next.length) return
    if (!selectedClass.value) {
      selectedClass.value = next[0].id
    }
  },
  { immediate: true }
)

// -----------------------------------------------------
// 工具函数
// -----------------------------------------------------
function getStudents(classId) {
  if (!classId) return []
  return studentState.value[classId] || []
}

function selectClass(id) {
  if (!authed.value) return
  if (selectedClass.value === id) return
  selectedClass.value = id
  emit('classChange', id)
}

function selectAddClass() {
  if (!authed.value) return
  selectedClass.value = ADD_CLASS_TAB
}

function isStudentSelected(id) {
  return selectedStudentIds.value.has(id)
}

function toggleSelection(id) {
  if (!props.selectionMode) return
  const next = new Set(selectedStudentIds.value)
  next.has(id) ? next.delete(id) : next.add(id)
  selectedStudentIds.value = next
  emit('update:modelValue', [...next])
}

function focusAddInput() {
  setTimeout(() => newStudentInput.value?.focus(), 20)
}

function handleAddButtonClick() {
  if (newStudentName.value.trim()) addStudent()
  else focusAddInput()
}

// -----------------------------------------------------
// 🔥🔥🔥 重做：addStudent（已对接数据库）
// -----------------------------------------------------
async function addStudent() {
  const cls = currentClass.value
  if (!cls) return
  const name = newStudentName.value.trim()
  if (!name) {
    actionMessage.value = '请输入学生姓名'
    return
  }

  try {
    const classId = selectedClass.value

    const resp = await apiFetch('/students/add', {
      method: 'POST',
      body: JSON.stringify({
        class_id: classId,
        student_name: name
      })
    })

    const added = normalizeStudent(resp)

    const updated = { ...studentState.value }
    const list = updated[classId] ? [...updated[classId]] : []
    list.push(added)
    updated[classId] = list
    studentState.value = updated

    newStudentName.value = ''
    actionMessage.value = `已添加 ${added.name}`
    focusAddInput()
  } catch (err) {
    console.error(err)
    actionMessage.value = '添加失败'
  }
}

// -----------------------------------------------------
// 🔥🔥🔥 重做：removeStudent（已对接数据库）
// -----------------------------------------------------
async function removeStudent(studentId) {
  if (!selectedClass.value) return
  const classId = selectedClass.value

  try {
    await apiFetch('/students/delete', {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId })
    })

    const list = studentState.value[classId] || []
    const removed = list.find((s) => s.id === studentId)

    studentState.value = {
      ...studentState.value,
      [classId]: list.filter((s) => s.id !== studentId)
    }

    actionMessage.value = removed ? `已删除 ${removed.name}` : '已删除学生'
  } catch (err) {
    console.error(err)
    actionMessage.value = '删除失败'
  }
}

// -----------------------------------------------------
// Excel 导入（你的原逻辑保留）
// -----------------------------------------------------
// 工具函数（你之前文件中原本存在，现在缺失的部分）
// -----------------------------------------------------

function calcNextId(map = {}) {
  let maxId = 0
  Object.values(map || {}).forEach((list) => {
    list.forEach((stu) => {
      if (stu.id > maxId) maxId = stu.id
    })
  })
  return maxId + 1
}

function calcNextClassId(list = []) {
  return (list || []).reduce((max, cls) => (cls.id > max ? cls.id : max), 0) + 1
}

function cloneStudents(data = {}) {
  const copy = {}
  Object.entries(data || {}).forEach(([classId, list]) => {
    copy[classId] = list.map((stu) => ({ ...stu }))
  })
  return copy
}

function cloneClasses(list = []) {
  return (list || []).map((cls) => normalizeClass(cls))
}

function normalizeClass(entry = {}) {
  return {
    id: entry.id ?? entry.class_id ?? entry.classId,
    name: entry.name ?? entry.class_name ?? entry.className ?? '未命名班级'
  }
}

function normalizeStudent(entry = {}) {
  return {
    id: entry.id ?? entry.student_id ?? entry.studentId,
    name: entry.name ?? entry.student_name ?? entry.studentName ?? ''
  }
}


// -----------------------------------------------------
// 班级加载
// -----------------------------------------------------
async function fetchClassesFromApi() {
  try {
    syncToken()
    if (!authed.value) {
      clearLocalState()
      return
    }

    const data = await apiFetch('/classes/list', { method: 'GET' })
    const normalized = (data || []).map((item) => normalizeClass(item))

    if (normalized.length) {
      hasSyncedClasses.value = true
      classList.value = normalized
      nextClassId.value = calcNextClassId(classList.value)
      studentState.value = {}

      selectedClass.value = normalized[0].id
      ensureStudentsLoaded(selectedClass.value)
    }
  } catch (error) {
    console.warn('班级数据同步失败', error)
  }
}


// -----------------------------------------------------
// 学生加载（每个班级）
// -----------------------------------------------------
async function ensureStudentsLoaded(classId) {
  if (!classId || classId === ADD_CLASS_TAB) return
  if (!authed.value) return
  if (Object.prototype.hasOwnProperty.call(studentState.value, classId)) return
  await fetchStudentsForClass(classId)
}

async function fetchStudentsForClass(classId) {
  if (!classId) return

  try {
    syncToken()
    if (!authed.value) {
      studentState.value = {}
      return
    }

    const data = await apiFetch(`/students/by_class?class_id=${classId}`, { method: 'GET' })
    const normalized = (data || []).map((item) => normalizeStudent(item))

    studentState.value = { ...studentState.value, [classId]: normalized }
    nextStudentId.value = calcNextId(studentState.value)
  } catch (error) {
    console.warn('学生数据同步失败', error)
  }
}


// -----------------------------------------------------
// Excel 处理（你的导入功能需要用到）
// -----------------------------------------------------

async function extractStudentNames(file) {
  const ext = (file.name.split('.').pop() || '').toLowerCase()
  if (['xlsx', 'xls', 'xlsm', 'xlsb'].includes(ext)) {
    return parseExcelFile(file)
  }
  const text = await file.text()
  return parseStudentNamesFromText(text)
}

async function parseExcelFile(file) {
  const XLSX = await loadXlsxModule()
  const data = await file.arrayBuffer()
  const workbook = XLSX.read(data, { type: 'array' })
  if (!workbook.SheetNames.length) {
    throw new Error('Excel 文件为空')
  }
  const sheet = workbook.Sheets[workbook.SheetNames[0]]
  const rows = XLSX.utils.sheet_to_json(sheet, { header: 1 })
  return parseRowsForNames(rows)
}

function parseStudentNamesFromText(text = '') {
  const rawRows = (text || '').split(/\r?\n/).map((row) => row.trim())
  const filtered = rawRows.filter(Boolean)
  if (!filtered.length) return []
  const delimiter = detectDelimiter(filtered[0])
  const rows = filtered.map((row) => splitRow(row, delimiter))
  return parseRowsForNames(rows)
}

function parseRowsForNames(rows = []) {
  const headerRowIndex = rows.findIndex((cols) =>
    cols.some((cell) => /姓名|name/i.test(String(cell || '').trim()))
  )
  if (headerRowIndex === -1) {
    throw new Error('模板缺少“姓名”列')
  }
  const headerRow = rows[headerRowIndex]
  const nameIndex = headerRow.findIndex((cell) => /姓名|name/i.test(String(cell || '').trim()))
  if (nameIndex === -1) {
    throw new Error('模板缺少“姓名”列')
  }
  const names = []
  for (let i = headerRowIndex + 1; i < rows.length; i++) {
    const name = String(rows[i][nameIndex] || '').trim()
    if (name) names.push(name)
  }
  return names
}

function detectDelimiter(row) {
  if (row.includes('\t')) return '\t'
  if (row.includes(';')) return ';'
  if (row.includes('|')) return '|'
  return ','
}

function splitRow(row, delimiter) {
  return row.split(delimiter).map((cell) => cell.trim())
}

let xlsxLoader
function loadXlsxModule() {
  if (!xlsxLoader) {
    xlsxLoader = import('https://cdn.jsdelivr.net/npm/xlsx@0.18.5/+esm')
  }
  return xlsxLoader
}


onMounted(() => {
  syncToken()
  if (!props.selectionMode && authed.value) {
    fetchClassesFromApi()
  }
})
</script>

<style scoped>
.class-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 14px 14px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 16px;
  background: radial-gradient(circle at top, rgba(59, 130, 246, 0.12), transparent 55%),
    rgba(15, 23, 42, 0.9);
  color: #e2e8f0;
}

.class-tabs {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 0;
  padding: 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
  overflow-x: auto;
}

.tab-btn {
  border: none;
  border-bottom: 3px solid transparent;
  background: transparent;
  color: rgba(226, 232, 240, 0.8);
  padding: 10px 18px 6px;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s ease, border-color 0.2s ease, background 0.2s ease;
  position: relative;
  font-weight: 600;
}

.tab-btn.add-class-tab {
  font-size: 18px;
  font-weight: 500;
  padding: 8px 12px 4px;
}

.tab-btn.active {
  color: #f8fafc;
  border-color: rgba(14, 165, 233, 0.9);
  background: linear-gradient(180deg, rgba(30, 41, 59, 0.5), rgba(15, 23, 42, 0.95));
}

.tab-btn:not(.active):hover {
  color: #cbd5f5;
  background: rgba(30, 41, 59, 0.3);
}

.tab-panel {
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-top: none;
  border-radius: 0 0 12px 12px;
  padding: 16px 14px;
  background: rgba(2, 6, 23, 0.35);
  min-height: 170px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.import-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 8px;
}

.import-panel label {
  font-size: 12px;
  color: rgba(226, 232, 240, 0.7);
}

.import-form {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.form-field {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.class-name-input {
  margin-top: 0;
}

.import-panel h4 {
  margin: 0;
  font-size: 16px;
}

.import-hint {
  margin: 0;
  color: rgba(226, 232, 240, 0.86);
}

.import-steps {
  margin: 0;
  padding-left: 18px;
  color: rgba(203, 213, 225, 0.9);
  font-size: 13px;
  line-height: 1.5;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border-radius: 10px;
  border: 1px solid rgba(14, 165, 233, 0.4);
  color: #e0f2fe;
  cursor: pointer;
  background: rgba(14, 165, 233, 0.12);
  font-weight: 600;
}

.upload-btn:hover {
  background: rgba(14, 165, 233, 0.2);
}

.file-select {
  cursor: pointer;
}

.file-hint,
.import-note {
  margin: 0;
  font-size: 12px;
  color: rgba(226, 232, 240, 0.75);
}

.confirm-btn {
  align-self: flex-start;
  margin-top: 4px;
  border: none;
  border-radius: 10px;
  padding: 8px 18px;
  background: linear-gradient(135deg, #22d3ee, #a855f7);
  color: #0f172a;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.confirm-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.error-text {
  margin: 0;
  color: #f87171;
  font-size: 12px;
}

.import-preview {
  margin: 0;
  color: #4ade80;
  font-size: 12px;
}

.roster-head {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.selection-head {
  justify-content: space-between;
  gap: 8px;
}
.badge {
  padding: 5px 12px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.25);
  color: #bfdbfe;
  font-size: 13px;
}

.badge.selected-badge {
  background: rgba(168, 85, 247, 0.18);
  color: #d8b4fe;
}

.badge.mini {
  font-size: 11px;
  padding: 3px 10px;
}

.roster-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
}

.student-card {
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 16px;
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: space-between;
  background: rgba(15, 23, 42, 0.82);
}

.student-card.selectable-card {
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.student-card.selected {
  border-color: rgba(168, 85, 247, 0.7);
  background: rgba(168, 85, 247, 0.12);
  transform: translateY(-1px);
}

.student-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.25);
  color: #c7d2fe;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.icon-btn {
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: transparent;
  color: #e2e8f0;
  border-radius: 12px;
  padding: 6px 10px;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease;
}

.icon-btn:hover {
  border-color: rgba(148, 163, 184, 0.8);
  color: #fff;
}

.icon-btn.remove-btn,
.icon-btn.add-btn {
  border: none;
  background: transparent;
}

.icon-btn.remove-btn:hover,
.icon-btn.add-btn:hover {
  border: none;
  color: #fff;
}

.add-card {
  border-style: dashed;
  opacity: 0.9;
}

.add-card .avatar {
  background: rgba(99, 102, 241, 0.25);
  color: #c7d2fe;
  border: none;
}

.inline-input {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(15, 23, 42, 0.85);
  color: #f8fafc;
  padding: 6px 8px;
  font-size: 13px;
  margin-top: 4px;
}

.add-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 28px;
  border-radius: 16px;
  border: 1px dashed rgba(148, 163, 184, 0.35);
  color: rgba(226, 232, 240, 0.6);
}

@media (max-width: 700px) {
  .add-form {
    flex-direction: column;
  }

  .add-form input,
  .add-form button {
    width: 100%;
  }
}
</style>
