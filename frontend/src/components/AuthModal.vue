<template>
  <div class="auth-backdrop" @click.self="emitClose">
    <div class="auth-modal">
      <header class="auth-header">
        <div class="titles">
          <h2>{{ isLogin ? '登录账号' : '注册新账号' }}</h2>
        </div>
        <button class="close-btn" type="button" @click="emitClose">×</button>
      </header>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <label class="field">
          <span>用户名 / 邮箱</span>
          <input
            v-model.trim="form.identifier"
            type="text"
            name="identifier"
            autocomplete="username"
            placeholder="如：teacher01 或 name@example.com"
            required
          />
        </label>

        <label class="field">
          <span>密码</span>
          <div class="input-wrapper">
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              name="password"
              autocomplete="current-password"
              minlength="6"
              placeholder="至少 6 位"
              required
            />
            <button
              type="button"
              class="toggle-visibility"
              :aria-label="showPassword ? '隐藏密码' : '显示密码'"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '🙈' : '👁' }}
            </button>
          </div>
        </label>

        <label v-if="isRegister" class="field">
          <span>确认密码</span>
          <div class="input-wrapper">
            <input
              v-model="form.confirm"
              :type="showConfirmPassword ? 'text' : 'password'"
              name="confirm"
              autocomplete="new-password"
              minlength="6"
              placeholder="再次输入密码"
              required
            />
            <button
              type="button"
              class="toggle-visibility"
              :aria-label="showConfirmPassword ? '隐藏确认密码' : '显示确认密码'"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              {{ showConfirmPassword ? '🙈' : '👁' }}
            </button>
          </div>
        </label>

        <label v-if="isRegister" class="field">
          <span>学校名称</span>
          <input
            v-model.trim="form.school_name"
            type="text"
            name="school_name"
            placeholder="请输入学校名称"
            required
          />
        </label>

        <label v-if="isRegister" class="field">
          <span>教学组名称</span>
          <input
            v-model.trim="form.group_name"
            type="text"
            name="group_name"
            placeholder="请输入教学组名称"
            required
          />
        </label>

        <p v-if="displayError" class="error">{{ displayError }}</p>

        <button class="primary" type="submit" :disabled="loading">
          {{ isLogin ? '登录' : '注册并登录' }}
        </button>
        <button
          class="ghost"
          type="button"
          @click="switchMode(isLogin ? 'register' : 'login')"
        >
          {{ isLogin ? '没有账号？注册一个' : '已有账号？返回登录' }}
        </button>
      </form>

      <p class="minor">点击提交即表示同意相关使用条款</p>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  mode: {
    type: String,
    default: 'login'
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'submit', 'mode-change'])

const form = reactive({
  identifier: '',
  password: '',
  confirm: '',
  school_name: '',
  group_name: ''
})
const localError = ref('')
const currentMode = ref(props.mode)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

watch(
  () => props.mode,
  (val) => {
    currentMode.value = val || 'login'
  }
)

const isLogin = computed(() => currentMode.value === 'login')
const isRegister = computed(() => currentMode.value === 'register')
const displayError = computed(() => localError.value || props.error)

function switchMode(next) {
  if (currentMode.value === next) return
  localError.value = ''
  currentMode.value = next
  emit('mode-change', next)
}

function emitClose() {
  emit('close')
}

function handleSubmit() {
  localError.value = ''
  if (isRegister.value && form.password !== form.confirm) {
    localError.value = '两次输入的密码不一致'
    return
  }
  if (isRegister.value && (!form.school_name || !form.group_name)) {
    localError.value = '学校名称和教学组名称为必填项'
    return
  }
  const payload = {
    mode: currentMode.value,
    identifier: form.identifier,
    password: form.password,
    school_name: form.school_name,
    group_name: form.group_name
  }
  emit('submit', payload)
}
</script>

<style scoped>
.auth-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 1000;
}

.auth-modal {
  width: min(420px, 95vw);
  background: linear-gradient(180deg, #0b1120, #0f172a);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 18px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  padding: 20px;
  color: #e2e8f0;
}

.auth-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.titles {
  flex: 1;
  text-align: center;
}

.titles h2 {
  margin: 2px 0 24px;
  font-size: 22px;
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(226, 232, 240, 0.7);
}

.subtext {
  margin: 0;
  color: rgba(148, 163, 184, 0.9);
  font-size: 13px;
}

.close-btn {
  border: none;
  background: rgba(255, 255, 255, 0.05);
  color: #e2e8f0;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  cursor: pointer;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
}

.field input {
  width: 100%;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(15, 23, 42, 0.7);
  color: #e2e8f0;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.7);
  padding-right: 6px;
}

.input-wrapper input {
  width: 100%;
  padding: 10px 12px;
  border: none;
  background: transparent;
  outline: none;
  color: #e2e8f0;
}

.toggle-visibility {
  border: none;
  background: rgba(15, 23, 42, 0.7);
  color: #e2e8f0;
  border-radius: 10px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 12px;
  min-width: 38px;
}

.primary {
  margin-top: 4px;
  border: none;
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  background: linear-gradient(135deg, #22d3ee, #a855f7);
  color: #0f172a;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s ease, opacity 0.15s ease;
}

.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.primary:not(:disabled):hover {
  transform: translateY(-1px);
}

.ghost {
  margin-top: 6px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  width: 100%;
  padding: 10px;
  border-radius: 12px;
  background: transparent;
  color: #e2e8f0;
  cursor: pointer;
}

.error {
  margin: 0;
  color: #f87171;
  font-size: 13px;
}

.minor {
  margin: 10px 0 0;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.8);
  text-align: center;
}
</style>
