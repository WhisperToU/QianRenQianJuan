import React, { useEffect, useMemo, useState } from "react";

const DEFAULT_BASE_URL = "http://127.0.0.1:5000";

// ------------------------
// 复制 Prompt 按钮组件
// ------------------------
function CopyPromptButton() {
  const promptText = `你是“千人千卷”物理题库的专属出题引擎。请严格遵守以下 LaTeX 规范生成题干和答案（LaTeX 正文）。教师不会编写 LaTeX，你需自动输出完全可用、可直接入库、可直接转换 Word 的规范内容。

【LaTeX 规范 v2.0】
1. 行内公式用 $...$；行间公式用 \\[...\\]；多行推导用 align。
2. 单位必须用 \\text{...}，如 4\\ \\text{s}、340\\ \\text{m/s}；禁止使用 \\mathrm、\\rm、siunitx。
3. 数字必须以普通数字形式书写，不得使用字体相关命令（如 \\mathrm、\\mathbf、\\mathit），以确保在 Word 中由默认数学字体（Times New Roman）渲染。
4. 允许：\\frac, \\sqrt, \\vec, \\cdot, \\times, 希腊字母, cases, align。
5. 禁止：\\newcommand, siunitx, physics 宏包命令, tikzpicture, 电路图宏包。
6. 公式推导的解释部分用普通文本；最终答案必须带单位并写成完整句子。
7. 不输出 markdown，不加 \`\`\`，只给纯 LaTeX。

【输出格式】
【题干（LaTeX 正文）】
（题干放这里）

【答案（LaTeX 正文）】
（答案放这里）

严格按规范生成题干和答案，不违反 LaTeX 标准，不使用任何未允许命令。`;

  const copy = () => {
    navigator.clipboard.writeText(promptText);
    alert("已复制出题 Prompt！");
  };

  return (
    <button
      onClick={copy}
      className="px-3 py-2 rounded bg-teal-600 hover:bg-teal-500 text-white"
    >
      复制出题 Prompt
    </button>
  );
}

// ------------------------
// 主组件
// ------------------------
export default function App() {
  const [baseUrl, setBaseUrl] = useState(DEFAULT_BASE_URL);
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const [query, setQuery] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({
    topic: "",
    difficulty_level: "easy",
    question_text: "",
    answer_text: "",
  });
  const [toast, setToast] = useState("");

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(""), 2200);
  };

  const fetchJSON = async (url, options = {}) => {
    const res = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  };

  const downloadBlob = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchJSON(`${baseUrl}/questions`);
      setQuestions(data);
    } catch (e) {
      console.error(e);
      showToast("加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [baseUrl]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return questions;
    return questions.filter(
      (x) =>
        String(x.question_id ?? "").includes(q) ||
        (x.topic || "").toLowerCase().includes(q) ||
        (x.difficulty_level || "").toLowerCase().includes(q) ||
        (x.question_text || "").toLowerCase().includes(q)
    );
  }, [questions, query]);

  const toggleOne = (id) => {
    const next = new Set(selected);
    next.has(id) ? next.delete(id) : next.add(id);
    setSelected(next);
  };

  const toggleAll = () => {
    if (selected.size === filtered.length)
      setSelected(new Set());
    else
      setSelected(new Set(filtered.map((x) => x.question_id)));
  };

  const doPrint = async (type) => {
    if (selected.size === 0) {
      showToast("先选择题目");
      return;
    }
    const ids = Array.from(selected);
    try {
      const res = await fetch(`${baseUrl}/printing/${type}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question_ids: ids }),
      });
      if (!res.ok) throw new Error(await res.text());
      const blob = await res.blob();
      downloadBlob(
        blob,
        type === "exam" ? "exam.docx" : "answers.docx"
      );
      showToast("已生成并下载");
    } catch (e) {
      console.error(e);
      showToast("生成失败");
    }
  };

  const openAdd = () => {
    setEditing(null);
    setForm({
      topic: "",
      difficulty_level: "easy",
      question_text: "",
      answer_text: "",
    });
    setModalOpen(true);
  };

  const openEdit = (q) => {
    setEditing(q);
    setForm({
      topic: q.topic || "",
      difficulty_level: q.difficulty_level || "easy",
      question_text: q.question_text || "",
      answer_text: q.answer_text || "",
    });
    setModalOpen(true);
  };

  const submitForm = async () => {
    try {
      if (editing) {
        await fetchJSON(
          `${baseUrl}/questions/${editing.question_id}`,
          {
            method: "PUT",
            body: JSON.stringify(form),
          }
        );
        showToast("已修改");
      } else {
        await fetchJSON(`${baseUrl}/questions`, {
          method: "POST",
          body: JSON.stringify(form),
        });
        showToast("已添加");
      }
      setModalOpen(false);
      await load();
    } catch (e) {
      console.error(e);
      showToast("提交失败");
    }
  };

  const del = async (q) => {
    if (!confirm(`确认删除题目 #${q.question_id} 吗？`)) return;
    try {
      await fetchJSON(`${baseUrl}/questions/${q.question_id}`, {
        method: "DELETE",
      });
      setSelected((prev) => {
        const s = new Set(prev);
        s.delete(q.question_id);
        return s;
      });
      await load();
      showToast("已删除");
    } catch (e) {
      console.error(e);
      showToast("删除失败");
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <h1 className="text-2xl font-bold">
            千人千卷 · 题库 & 打印
          </h1>

          <div className="flex items-center gap-2">
            <input
              className="px-3 py-2 rounded bg-neutral-900 border border-neutral-800 w-80"
              placeholder="后端基址，例如 http://127.0.0.1:5000"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
            />
            <button
              onClick={load}
              className="px-3 py-2 rounded bg-neutral-800 hover:bg-neutral-700 border border-neutral-700"
            >
              连接
            </button>
          </div>
        </header>

        {/* 操作区 */}
        <section className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <input
              className="pl-9 pr-3 py-2 rounded bg-neutral-900 border border-neutral-800 w-80"
              placeholder="搜索：ID/主题/难度/正文关键词"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <span className="absolute left-3 top-2.5 text-neutral-500">
              🔎
            </span>
          </div>

          <button
            onClick={openAdd}
            className="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-500"
          >
            新增题目
          </button>

          {/* 复制 Prompt 按钮 */}
          <CopyPromptButton />

          <div className="ml-auto flex gap-2">
            <button
              onClick={() => doPrint("exam")}
              className="px-3 py-2 rounded bg-indigo-600 hover:bg-indigo-500"
            >
              生成试卷
            </button>
            <button
              onClick={() => doPrint("answers")}
              className="px-3 py-2 rounded bg-fuchsia-600 hover:bg-fuchsia-500"
            >
              生成答案
            </button>
          </div>
        </section>

        {/* 表格 */}
        <section className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-neutral-900/60 sticky top-0 z-10">
                <tr className="text-left">
                  <th className="px-4 py-3 w-12">
                    <input
                      type="checkbox"
                      onChange={toggleAll}
                      checked={
                        selected.size === filtered.length &&
                        filtered.length > 0
                      }
                    />
                  </th>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">主题</th>
                  <th className="px-4 py-3">难度</th>
                  <th className="px-4 py-3">创建时间</th>
                  <th className="px-4 py-3">题干（预览）</th>
                  <th className="px-4 py-3 w-44">操作</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-neutral-800">
                {loading && (
                  <tr>
                    <td
                      colSpan={7}
                      className="px-4 py-6 text-center text-neutral-400"
                    >
                      加载中…
                    </td>
                  </tr>
                )}

                {!loading && filtered.length === 0 && (
                  <tr>
                    <td
                      colSpan={7}
                      className="px-4 py-6 text-center text-neutral-500"
                    >
                      无数据
                    </td>
                  </tr>
                )}

                {!loading &&
                  filtered.map((q) => (
                    <tr
                      key={q.question_id}
                      className="hover:bg-neutral-800/50"
                    >
                      <td className="px-4 py-3 align-top">
                        <input
                          type="checkbox"
                          checked={selected.has(q.question_id)}
                          onChange={() => toggleOne(q.question_id)}
                        />
                      </td>

                      <td className="px-4 py-3 align-top">
                        {q.question_id}
                      </td>
                      <td className="px-4 py-3 align-top">{q.topic}</td>
                      <td className="px-4 py-3 align-top">
                        {q.difficulty_level}
                      </td>
                      <td className="px-4 py-3 align-top">
                        {q.created_at
                          ?.slice(0, 19)
                          .replace("T", " ") || "-"}
                      </td>

                      <td className="px-4 py-3 align-top max-w-xl">
                        <div className="line-clamp-3 text-neutral-300 whitespace-pre-wrap break-words">
                          {q.question_text}
                        </div>
                      </td>

                      <td className="px-4 py-3 align-top">
                        <div className="flex gap-2">
                          <button
                            onClick={() => openEdit(q)}
                            className="px-2 py-1 rounded bg-neutral-800 hover:bg-neutral-700"
                          >
                            编辑
                          </button>
                          <button
                            onClick={() => del(q)}
                            className="px-2 py-1 rounded bg-rose-700 hover:bg-rose-600"
                          >
                            删除
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </section>

        <footer className="text-xs text-neutral-500">
          当前后端：{baseUrl} · 已选 {selected.size} 条
        </footer>
      </div>

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black/60 grid place-items-center p-4 z-50">
          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl w-full max-w-3xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">
                {editing
                  ? `编辑题目 #${editing.question_id}`
                  : "新增题目"}
              </h2>
              <button
                onClick={() => setModalOpen(false)}
                className="text-neutral-400 hover:text-neutral-200"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm text-neutral-400">主题</label>
                <input
                  className="w-full px-3 py-2 rounded bg-neutral-900 border border-neutral-800"
                  value={form.topic}
                  onChange={(e) =>
                    setForm({ ...form, topic: e.target.value })
                  }
                />
              </div>

              <div className="space-y-1">
                <label className="text-sm text-neutral-400">难度</label>
                <select
                  className="w-full px-3 py-2 rounded bg-neutral-900 border border-neutral-800"
                  value={form.difficulty_level}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      difficulty_level: e.target.value,
                    })
                  }
                >
                  <option value="easy">easy</option>
                  <option value="medium">medium</option>
                </select>
              </div>

              <textarea
                rows={8}
                className="w-full px-3 py-2 rounded bg-neutral-900 border border-neutral-800 font-mono"
                value={form.question_text}
                onChange={(e) =>
                  setForm({
                    ...form,
                    question_text: e.target.value,
                  })
                }
              ></textarea>

              <div className="md:col-span-2 space-y-1">
                <label className="text-sm text-neutral-400">
                  答案（LaTeX 正文，可留空）
                </label>
                <textarea
                  rows={6}
                  className="w-full px-3 py-2 rounded bg-neutral-900 border border-neutral-800 font-mono"
                  value={form.answer_text}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      answer_text: e.target.value,
                    })
                  }
                />
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <button
                onClick={() => setModalOpen(false)}
                className="px-3 py-2 rounded bg-neutral-800 hover:bg-neutral-700"
              >
                取消
              </button>
              <button
                onClick={submitForm}
                className="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-500"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}

      {toast && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-neutral-800 text-neutral-100 border border-neutral-700 rounded-full px-4 py-2 text-sm">
          {toast}
        </div>
      )}
    </div>
  );
}
