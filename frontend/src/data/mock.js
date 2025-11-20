export const mockTopics = [
  { id: 101, name: '函数与图像' },
  { id: 102, name: '多项式与因式分解' },
  { id: 103, name: '一元二次方程' },
  { id: 104, name: '几何与坐标' },
  { id: 105, name: '数列与归纳' },
  { id: 106, name: '概率与统计' }
];

export const mockClasses = [
  { id: 2, name: '2年级' },
  { id: 4, name: '4年级' },
  { id: 5, name: '5年级' }
];

export const mockStudents = {
  2: [
    { id: 1, name: '周老师' },
    { id: 2, name: '赵静' },
    { id: 3, name: '李明' },
    { id: 4, name: '陈浩' }
  ],
  4: [
    { id: 61, name: '王乐' },
    { id: 62, name: '刘星' },
    { id: 63, name: '张清' }
  ],
  5: [
    { id: 91, name: '邓宇' },
    { id: 92, name: '韩悦' },
    { id: 93, name: '史辰' }
  ]
};

export const mockOverview = {
  totalTopics: mockTopics.length,
  totalQuestions: 38,
  tables: ['questions', 'classes', 'students', 'assigned_questions'],
  topics: [
    {
      name: '函数与图像',
      count: 12,
      difficulties: {
        easy: {
          count: 4,
          sample: '判断函数 y = x^2 + 1 的图像的位置'
        },
        medium: {
          count: 5,
          sample: '求非负实数范围内函数的最大值'
        },
        difficult: {
          count: 3,
          sample: '结合导数近似判断函数单调区间'
        }
      }
    },
    {
      name: '多项式与因式分解',
      count: 8,
      difficulties: {
        easy: {
          count: 3,
          sample: '分解 (x^2 - 1)(x + 3)'
        },
        medium: {
          count: 3,
          sample: '判断多项式在实数集上的符号'
        },
        difficult: {
          count: 2,
          sample: '利用根与系数关系构造二次方程'
        }
      }
    }
  ]
};

const baseQuestionBank = [
  {
    question_id: 201,
    title: '函数单调性判定',
    topic: '函数与图像',
    topic_id: 101,
    difficulty: 'easy',
    question:
      '已知函数 f(x) = 2x^2 - 4x + 3，判断其在区间 [-1, 3] 上的单调性，并说明理由。',
    answer: '函数为开口向上的抛物线，顶点在 x=1，区间 [-1,3] 包含顶点，需分区间分析。',
    question_image: 'https://via.placeholder.com/360x180?text=函数图像',
    type: '解答题',
    duration: 8
  },
  {
    question_id: 202,
    title: '多项式因式分解',
    topic: '多项式与因式分解',
    topic_id: 102,
    difficulty: 'medium',
    question:
      '将多项式 x^3 - 3x^2 + 4x - 12 分解因式，并写出所有实数根。',
    answer: '先提取公因式 (x - 3)，再分解剩余 x^2 + 4，根为 3。',
    question_image: '',
    type: '计算题',
    duration: 6
  },
  {
    question_id: 203,
    title: '一元二次应用题',
    topic: '一元二次方程',
    topic_id: 103,
    difficulty: 'medium',
    question:
      '一条绳子折成两段，短段长为 x，长段为 5x，两段围成的矩形周长为 24，求两段长度。',
    answer: '设长为 5x，短为 x，两段总长 6x=24，x=4，长段 20，短段 4。',
    question_image: 'https://via.placeholder.com/360x180?text=%E7%9F%A5%E5%AE%9A%E7%9F%A9%E5%BD%A2',
    type: '应用题',
    duration: 10
  },
  {
    question_id: 204,
    title: '几何图形分析',
    topic: '几何与坐标',
    topic_id: 104,
    difficulty: 'difficult',
    question:
      '在坐标平面上，垂直平分线与直线 y = 2x + 1 的交点坐标是多少？',
    answer: '计算垂直平分线方程：斜率 -1/2，设点 (x,y)，联立求出交点。',
    question_image: '',
    type: '推理题',
    duration: 12
  },
  {
    question_id: 205,
    title: '数列递推',
    topic: '数列与归纳',
    topic_id: 105,
    difficulty: 'easy',
    question:
      '数列 a_n 满足 a_1=2，a_{n+1}=3a_n+2，求 a_3 的值及通项表达式。',
    answer: 'a_2=8，a_3=26。通项为 a_n = (3^n - 1)。',
    question_image: '',
    type: '计算题',
    duration: 6
  },
  {
    question_id: 206,
    title: '概率判断',
    topic: '概率与统计',
    topic_id: 106,
    difficulty: 'difficult',
    question:
      '从 3 个红球和 2 个蓝球中不放回抽取 2 个球，求恰有 1 个蓝球的概率。',
    answer: '共有 C(5,2)=10 种，包含 1 蓝的为 3×2=6，概率 6/10=3/5。',
    question_image: '',
    type: '选择题',
    duration: 7
  }
];

export function generateMockQuestions(count = 4) {
  const normalizedCount = Math.max(1, Math.min(count, 6));
  return Array.from({ length: normalizedCount }).map((_, index) => {
    const template = baseQuestionBank[index % baseQuestionBank.length];
    return {
      uid: `mock-${template.question_id}-${index}`,
      question_id: template.question_id + index,
      persisted: false,
      saved: false,
      title: template.title,
      topic: template.topic,
      topic_id: template.topic_id,
      difficulty: template.difficulty,
      question: template.question,
      answer: template.answer,
      question_image: template.question_image,
      type: template.type,
      duration: template.duration
    };
  });
}
