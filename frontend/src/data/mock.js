export const mockTopics = ['分数四则运算', '函数与图像', '几何思维', '概率初步'];

export const mockClasses = [
  { id: '1', name: '五年级一班' },
  { id: '2', name: '五年级三班' }
];

export const mockStudents = {
  '1': [
    { id: 1, name: '张星辰' },
    { id: 2, name: '李安同' },
    { id: 3, name: '黄可盈' }
  ],
  '2': [
    { id: 4, name: '周瑾瑜' },
    { id: 5, name: '秦慧雯' },
    { id: 6, name: '罗煊' }
  ]
};

export const mockOverview = {
  totalTopics: 7,
  totalQuestions: 214,
  tables: ['questions', 'assigned_questions', 'students', 'classes', 'student_records'],
  topics: [
    {
      name: '分数四则运算',
      count: 48,
      difficulties: {
        easy: { count: 18, sample: '求 3/5 + 2/7，写出化简过程' },
        medium: { count: 20, sample: '解方程：x - 2/3 = 1/4，并分析常见错误' },
        hard: { count: 10, sample: '若 a/b + c/d = 1，求最简分数组合' }
      }
    },
    {
      name: '函数与图像',
      count: 36,
      difficulties: {
        easy: { count: 12, sample: '已知 y = 2x，求 x=5 时的 y' },
        medium: { count: 15, sample: '画出 y = |x-2| 图像并说明关键点' },
        hard: { count: 9, sample: '讨论 y=x^2+kx+3 在 x>0 的单调性' }
      }
    }
  ]
};

export function generateMockQuestions(count = 4) {
  return Array.from({ length: count }).map((_, idx) => ({
    id: idx + 1,
    title: `题目 ${idx + 1}`,
    topic: mockTopics[idx % mockTopics.length],
    difficulty: ['easy', 'medium', 'medium', 'hard'][idx % 4],
    question: `第 ${idx + 1} 题：请完成 ${mockTopics[idx % mockTopics.length]} 的练习。`,
    answer: `参考答案：这是第 ${idx + 1} 题的解析。`
  }));
}
