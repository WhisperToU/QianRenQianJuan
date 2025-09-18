# 千人千卷 (AI-Driven Personalized Homework System)

本项目是一个 **AI驱动的个性化作业系统**，旨在为大班额环境下的中学课堂提供低成本的因材施教解决方案。  
系统围绕 **出题、组卷、批改、答案打印** 四个核心环节，帮助教师快速生成并管理每位学生的个性化作业。由于是poc测试，所以这四个核心环节还没有集中成一个系统。

本项目最初应用于雅安市成实外高级中学的教学实验，并在论文  
《基于AI批量出题的低成本因材施教研究报告》中完整介绍了系统设计与实践成果。

---

## 📌 核心功能

### 1. 出题系统（`/question/`）
- 题目展示（难度区分背景颜色）
- 新增、编辑、删除题目
- 支持答案折叠/展开
- 响应式布局与复制提示
- 技术：PHP + MySQL + HTML5 + CSS3 + JavaScript (ES6)

### 2. 个性化组卷系统（`/textpaper/`）
- 学生选择与分组
- 按难度、主题生成个性化试卷
- 记录学生做题历史，避免重复
- 自动生成 Word 文档（Python-docx）
- 技术：Flask (Python) + MySQL + HTML/JS

### 3. 批改系统（`/correcting/`）
- 学生作业按日期筛选
- 单题展示与逐题批改
- 评分与文字反馈保存至数据库
- 键盘快捷切换题目
- 自动生成答案汇总（Python 脚本）
- 技术：PHP + MySQL + Python

---

## 🛠️ 技术栈

- **前端**：HTML5, CSS3, JavaScript (ES6)
- **后端**：PHP, Flask (Python)
- **数据库**：MySQL
- **辅助工具**：Python-docx (生成试卷与答案)

---

## 📂 项目结构

```
├── question/ # 出题系统 (PHP)
│ ├── index.php
│ ├── api.php
│ └── config.php
│
├── textpaper/ # 个性化组卷系统 (Flask + Python)
│ ├── index.html
│ └── server.py
│
├── correcting/ # 批改系统 (PHP + Python)
│ ├── index.php
│ ├── api.php
│ ├── config.php
│ ├── style.css
│ ├── save_feedback.php
│ └── printAnswer.py
│
├── teaching_assistant.sql/ # 数据库信息
│
├── 界面截图及poc报告
│ ├── correcting界面.png
│ ├── question界面.png
│ ├── text peaper界面.png
│ └── report.pdf
│
└── README.md
```

---

## 📖 教学实验与成果

- 出题效率提升 **70%**  
- 题目命制正确率提升 **11%**  
- 作业难度适配性提高 **13.1%**  
- 学生深度参与度提高 **44.3%**  
- 特别对 **中上游学生** 帮助显著

详情见论文《基于AI批量出题的低成本因材施教研究报告》（见 `/docs/report.pdf`）。

---

## 🚀 本地运行说明

1. 请下载 zip 后在本地解压，包含 question/ textpaper/ correcting 三个模块。
2. 安装 [phpStudy](https://www.xp.cn/)（用于运行 PHP + MySQL）
3. 配置数据库（参考 `/question/config.php` 和 `/correcting/config.php`）
4. 打开 `phpStudy`，运行 `/question` 与 `/correcting`
5. 使用 VSCode 运行 `/textpaper/server.py`
6. 在浏览器中访问 `http://localhost/...` 即可使用

---

## 📌 未来优化方向

- 将现有 Python 功能（组卷、答案打印等）逐步迁移到 PHP，实现技术栈统一
- 三个子系统合并为统一网站
- 自动批改模块
- AI讲题模块
- 在线部署（支持公网访问）

---

## ✅ 教学落地价值

不同于市面上依赖昂贵硬件或与课堂脱节的解决方案，本项目由一线教师主导设计，  
并配套了完整的 **“出题 → 批改 → 改错 → 再反馈” 教学闭环**。  

在真实课堂实验中：  
- 系统出题效率提升 **70%**  
- 学生作业适配性提高 **13.1%**  
- 学生深度参与度提高 **44.3%**  
- 特别对中上游学生帮助显著  

👉 详见 `/界面截图及poc报告/report.pdf`（《基于AI批量出题的低成本因材施教研究报告》）。
