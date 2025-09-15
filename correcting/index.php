<?php
//完善version5的编辑功能
//bug：version2的姓氏bug没有修复。
require_once 'config.php';

// 拼音转换函数
function getPinyin($name) {
    $pinyinMap = [
        '罗' => 'l', '杨' => 'y', '唐' => 't', '何' => 'h', '寇' => 'k',
        '周' => 'z', '孙' => 's', '宋' => 's', '岑' => 'c', '张' => 'z',
        '陈' => 'c', '王' => 'w', '万' => 'w', '古' => 'g', '李' => 'l',
        '郑' => 'z', '谢' => 'x', '代' => 'd', '柳' => 'l', '刘' => 'l',
        '程' => 'c', '高' => 'g', '叶' => 'y', '吴' => 'w', '牟' => 'm',
        '彭' => 'p', '卢' => 'l', '范' => 'f'
    ];
    
    $firstChar = mb_substr($name, 0, 1, 'UTF-8');
    return isset($pinyinMap[$firstChar]) ? $pinyinMap[$firstChar] : $firstChar;
}

// 获取日期参数，默认为当天
$selectedDate = isset($_GET['date']) ? $_GET['date'] : date('Y-m-d');

// 从数据库获取学生数据
$students = [];
$studentQuestions = [];

// 获取所有学生
$studentQuery = $conn->query("SELECT student_id, student_name FROM students");
while ($row = $studentQuery->fetch_assoc()) {
    $students[$row['student_id']] = $row['student_name'];
}

// 获取每个学生的题目（根据选择的日期）
foreach ($students as $student_id => $student_name) {
    $questionQuery = $conn->prepare("
        SELECT DISTINCT question_id 
        FROM student_records 
        WHERE student_id = ? 
        AND DATE(create_at) = ?
    ");
    $questionQuery->bind_param('is', $student_id, $selectedDate);
    $questionQuery->execute();
    $result = $questionQuery->get_result();
    
    $questionIds = [];
    while ($row = $result->fetch_assoc()) {
        $questionIds[] = $row['question_id'];
    }
    
    if (!empty($questionIds)) {
        $studentQuestions[$student_name] = $questionIds;
    }
    
    $questionQuery->close();
}

// 按拼音首字母分组学生
$groupedStudents = [
    'A-C' => [],
    'D-F' => [],
    'G-K' => [],
    'L' => [],
    'M-P' => [],
    'Q-S' => [],
    'T-W' => [],
    'X-Y' => [],
    'Z' => []
];

// 定义分组规则
$groupRules = [
    'A-C' => ['a','b','c'],
    'D-F' => ['d','e','f'],
    'G-K' => ['g','h','j','k'],
    'L' => ['l'],
    'M-P' => ['m','n','o','p'],
    'Q-S' => ['q','r','s'],
    'T-W' => ['t','u','v','w'],
    'X-Y' => ['x','y'],
    'Z' => ['z']
];

foreach ($studentQuestions as $name => $ids) {
    $pinyinInitial = strtolower(getPinyin($name));
    
    // 确定分组
    $group = 'T-Z'; // 默认分组
    foreach ($groupRules as $groupName => $initials) {
        if (in_array($pinyinInitial, $initials)) {
            $group = $groupName;
            break;
        }
    }
    
    $groupedStudents[$group][$name] = $ids;
}

// 按学生姓名排序每个分组
foreach ($groupedStudents as &$group) {
    ksort($group);
}
unset($group);

// 移除空的分组
$groupedStudents = array_filter($groupedStudents, function($group) {
    return !empty($group);
});

// 处理学生选择
$selectedStudent = isset($_GET['student']) ? $_GET['student'] : '';
$questions = [];
$currentQuestionIndex = isset($_GET['q']) ? (int)$_GET['q'] : 0;

if ($selectedStudent && isset($studentQuestions[$selectedStudent])) {
    $questionIds = $studentQuestions[$selectedStudent];
    $placeholders = implode(',', array_fill(0, count($questionIds), '?'));
    $types = str_repeat('i', count($questionIds));
    
    $stmt = $conn->prepare("SELECT * FROM questions WHERE question_id IN ($placeholders)");
    $stmt->bind_param($types, ...$questionIds);
    $stmt->execute();
    $result = $stmt->get_result();
    
    while ($row = $result->fetch_assoc()) {
        $questions[] = $row;
    }
    
    $stmt->close();
    
    // 确保当前题目索引有效
    if ($currentQuestionIndex < 0 || $currentQuestionIndex >= count($questions)) {
        $currentQuestionIndex = 0;
    }
    
    // 获取当前问题的记录ID和学生ID
    if (!empty($questions)) {
        $currentQuestionId = $questions[$currentQuestionIndex]['question_id'];
        $studentId = array_search($selectedStudent, $students);
        
        $recordQuery = $conn->prepare("
            SELECT record_id, performance_score 
            FROM student_records 
            WHERE student_id = ? 
            AND question_id = ?
            AND DATE(create_at) = ?
            LIMIT 1
        ");
        $recordQuery->bind_param('iis', $studentId, $currentQuestionId, $selectedDate);
        $recordQuery->execute();
        $recordResult = $recordQuery->get_result();
        $currentRecord = $recordResult->fetch_assoc();
        $recordQuery->close();
    }
}
?>

<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学生作业批改系统</title>
    <link rel="stylesheet" href="style.css">
    <style>
        .date-picker {
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        .date-picker label {
            margin-right: 10px;
            font-weight: bold;
        }
        .date-picker input {
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .date-picker button {
            margin-left: 10px;
            padding: 5px 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .date-picker button:hover {
            background-color: #45a049;
        }
        
        /* 新增的评分样式 */
        .feedback-container {
            display: flex;
            align-items: center;
            margin-top: 10px;
            gap: 10px;
        }
        .feedback-input {
            flex: 1;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .save-feedback {
            padding: 8px 15px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .save-feedback:hover {
            background-color: #45a049;
        }
        .score-select {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        /* 新增编辑模式样式 */
        .edit-mode {
            border: 2px solid #4CAF50;
            background-color: #f9f9f9;
        }
        
        .editable-content {
            border: 1px solid #ddd;
            padding: 10px;
            min-height: 100px;
            margin: 10px 0;
            background-color: white;
            outline: none;
        }
        
        .editable-content:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
        }
        
        .toolbar {
            margin-bottom: 10px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .toolbar button {
            padding: 6px 12px;
            border: 1px solid #555;
            border-radius: 4px;
            cursor: pointer;
            background-color: #555;
            color: white;
            font-weight: bold;
            transition: all 0.2s;
        }
        
        .toolbar button:hover {
            background-color: #333;
        }
        
        .toolbar small {
            color: #666;
        }
        
        .toolbar-separator {
            width: 1px;
            height: 20px;
            background-color: #999;
            margin: 0 5px;
        }
        
        .edit-controls {
            margin-top: 15px;
            text-align: right;
        }
        
        .edit-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .save-btn {
            background-color: #4CAF50;
            color: white;
        }
        
        .cancel-btn {
            background-color: #6c757d;
            color: white;
            margin-left: 10px;
        }
        
        /* 图片上传样式 */
        .image-upload-container {
            margin: 15px 0;
            padding: 15px;
            border: 1px dashed #ccc;
            border-radius: 4px;
            background-color: #f8f9fa;
        }
        
        .image-upload-label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
        }
        
        .image-preview {
            max-width: 100%;
            max-height: 200px;
            margin-top: 10px;
            display: none;
        }
        
        .remove-image {
            margin-left: 10px;
            color: #dc3545;
            cursor: pointer;
        }
        
        .current-image {
            max-width: 100%;
            max-height: 200px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>学生作业批改系统</h1>
        
        <div class="layout">
            <!-- 左侧学生列表 -->
            <div class="student-panel">
                <div class="date-picker">
                    <label for="dateSelect">选择日期:</label>
                    <input type="date" id="dateSelect" value="<?php echo htmlspecialchars($selectedDate); ?>">
                    <button id="applyDate">应用</button>
                </div>
                <div class="search-box">
                    <input type="text" id="studentSearch" placeholder="输入姓名或拼音首字母搜索..." autocomplete="off">
                </div>
                <div class="student-groups" id="studentGroups">
                    <?php foreach ($groupedStudents as $groupName => $group): ?>
                        <div class="student-group">
                            <h3 class="group-title" data-count="<?php echo count($group); ?>"><?php echo htmlspecialchars($groupName); ?></h3>
                            <div class="student-list">
                                <?php foreach ($group as $name => $ids): ?>
                                    <a href="?date=<?php echo urlencode($selectedDate); ?>&student=<?php echo urlencode($name); ?>" 
                                       class="student-item <?php if ($selectedStudent === $name) echo 'active'; ?>"
                                       data-name="<?php echo htmlspecialchars($name); ?>"
                                       data-pinyin="<?php echo htmlspecialchars(getPinyin($name)); ?>">
                                        <?php echo htmlspecialchars($name); ?>
                                    </a>
                                <?php endforeach; ?>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
                <div class="panel-actions">
                    <button id="resetMarked">重置批改状态</button>
                    <div class="marked-sequence" id="markedSequence">
                        <h4>已批改学生顺序</h4>
                        <div id="sequenceList"></div>
                        <button class="export-btn" id="exportSequence">导出顺序</button>
                    </div>
                </div>
            </div>
            
            <!-- 右侧题目内容 -->
            <div class="content-panel">
                <?php if ($selectedStudent): ?>
                    <div class="student-header">
                        <h2><?php echo htmlspecialchars($selectedStudent); ?> 第<?php echo $currentQuestionIndex + 1; ?>题</h2>
                        <?php if (!empty($questions)): ?>
                        <div class="feedback-container">
                            <select class="score-select" id="performanceScore">
                                <option value="">选择评分</option>
                                <option value="1" <?php if (isset($currentRecord['performance_score']) && $currentRecord['performance_score'] == '1') echo 'selected'; ?>>1分</option>
                                <option value="2" <?php if (isset($currentRecord['performance_score']) && $currentRecord['performance_score'] == '2') echo 'selected'; ?>>2分</option>
                                <option value="3" <?php if (isset($currentRecord['performance_score']) && $currentRecord['performance_score'] == '3') echo 'selected'; ?>>3分</option>
                                <option value="4" <?php if (isset($currentRecord['performance_score']) && $currentRecord['performance_score'] == '4') echo 'selected'; ?>>4分</option>
                                <option value="5" <?php if (isset($currentRecord['performance_score']) && $currentRecord['performance_score'] == '5') echo 'selected'; ?>>5分</option>
                            </select>
                            <input type="text" class="feedback-input" id="studentFeedback" placeholder="输入反馈..." value="<?php echo isset($currentRecord['student_feedback']) ? htmlspecialchars($currentRecord['student_feedback']) : ''; ?>">
                            <button class="save-feedback" id="saveFeedback">保存</button>
                        </div>
                        <?php endif; ?>
                    </div>
                    
                    <?php if (!empty($questions)): ?>
                        <div class="questions-container">
                            <?php 
                            $question = $questions[$currentQuestionIndex];
                            ?>
                            <div class="question active" data-question-id="<?php echo $question['question_id']; ?>">
                                <div class="question-meta">
                                    <span class="question-id">题目 ID: <?php echo $question['question_id']; ?></span>
                                    <span class="difficulty <?php echo strtolower($question['difficulty_level']); ?>">
                                        <?php echo $question['difficulty_level']; ?>
                                    </span>
                                    <span class="topic">主题: <?php echo htmlspecialchars($question['topic']); ?></span>
                                    <button class="edit-btn" id="editQuestionBtn" style="float: right;">编辑题目</button>
                                </div>
                                
                                <div class="question-content">
                                    <div class="question-text">
                                        <h4>题目内容</h4>
                                        <div class="html-content"><?php echo $question['question_text']; ?></div>
                                    </div>
                                    <?php if (!empty($question['question_image'])): ?>
                                        <img src="<?php echo htmlspecialchars($question['question_image']); ?>" alt="题目图片" class="current-image">
                                    <?php endif; ?>
                                </div>
                                
                                <div class="answer-content">
                                    <h4>参考答案</h4>
                                    <div class="html-content"><?php echo $question['answer_text']; ?></div>
                                </div>
                            </div>
                        </div>
                    <?php else: ?>
                        <div class="no-questions">
                            <p>没有找到该学生的题目信息。</p>
                        </div>
                    <?php endif; ?>
                <?php else: ?>
                    <div class="welcome-message">
                        <h2>欢迎使用作业批改系统</h2>
                        <p>请从左侧选择学生查看对应的题目</p>
                        <p class="date-info">当前日期: <?php echo htmlspecialchars($selectedDate); ?></p>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <script>
        // 日期选择功能
        document.addEventListener('DOMContentLoaded', function() {
            const dateSelect = document.getElementById('dateSelect');
            const applyDateBtn = document.getElementById('applyDate');
            
            // 应用日期筛选
            applyDateBtn.addEventListener('click', function() {
                const selectedDate = dateSelect.value;
                window.location.href = `?date=${selectedDate}`;
            });
            
            // 键盘导航功能
            document.addEventListener('keydown', function(event) {
                const selectedStudent = '<?php echo $selectedStudent; ?>';
                const questionCount = <?php echo isset($questions) ? count($questions) : 0; ?>;
                const currentIndex = <?php echo $currentQuestionIndex; ?>;
                const selectedDate = '<?php echo $selectedDate; ?>';
                
                if (!selectedStudent || questionCount <= 1) return;
                
                if (event.key === 'ArrowLeft' && currentIndex > 0) {
                    // 左箭头 - 上一题
                    window.location.href = `?date=${selectedDate}&student=${encodeURIComponent(selectedStudent)}&q=${currentIndex - 1}`;
                } else if (event.key === 'ArrowRight' && currentIndex < questionCount - 1) {
                    // 右箭头 - 下一题
                    window.location.href = `?date=${selectedDate}&student=${encodeURIComponent(selectedStudent)}&q=${currentIndex + 1}`;
                }
            });

            // 搜索和批改功能
            const searchInput = document.getElementById('studentSearch');
            const studentItems = document.querySelectorAll('.student-item');
            const resetMarkedButton = document.getElementById('resetMarked');
            const sequenceList = document.getElementById('sequenceList');
            const exportButton = document.getElementById('exportSequence');
            
            // 保存反馈功能
            const saveFeedbackBtn = document.getElementById('saveFeedback');
            if (saveFeedbackBtn) {
                saveFeedbackBtn.addEventListener('click', function() {
                    const score = document.getElementById('performanceScore').value;
                    const feedback = document.getElementById('studentFeedback').value;
                    const studentId = <?php echo isset($studentId) ? $studentId : 'null'; ?>;
                    const questionId = <?php echo isset($currentQuestionId) ? $currentQuestionId : 'null'; ?>;
                    const recordId = <?php echo isset($currentRecord['record_id']) ? $currentRecord['record_id'] : 'null'; ?>;
                    const date = '<?php echo $selectedDate; ?>';
                    
                    if (!studentId || !questionId) {
                        alert('无法保存反馈: 缺少学生或题目信息');
                        return;
                    }
                    
                    // 发送AJAX请求保存反馈
                    const formData = new FormData();
                    formData.append('student_id', studentId);
                    formData.append('question_id', questionId);
                    formData.append('performance_score', score);
                    formData.append('student_feedback', feedback);
                    formData.append('date', date);
                    if (recordId) formData.append('record_id', recordId);
                    
                    fetch('save_feedback.php', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('反馈保存成功');
                            // 自动标记为已批改
                            const currentStudent = document.querySelector('.student-item.active');
                            if (currentStudent) {
                                const name = currentStudent.dataset.name;
                                if (!markedStudents.includes(name)) {
                                    markedStudents.push(name);
                                    markedSequence.push(name);
                                    localStorage.setItem('markedStudents', JSON.stringify(markedStudents));
                                    localStorage.setItem('markedSequence', JSON.stringify(markedSequence));
                                    updateDisplay();
                                }
                            }
                        } else {
                            alert('保存失败: ' + (data.message || '未知错误'));
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('保存失败: ' + error.message);
                    });
                });
            }
            
            // 加载已批改学生
            let markedStudents = JSON.parse(localStorage.getItem('markedStudents')) || [];
            let markedSequence = JSON.parse(localStorage.getItem('markedSequence')) || [];
            
            // 更新显示
            function updateDisplay() {
                studentItems.forEach(item => {
                    const name = item.dataset.name;
                    if (markedStudents.includes(name)) {
                        item.style.display = 'none';
                    } else {
                        item.style.display = '';
                    }
                });
                
                // 更新分组计数
                updateGroupCounts();
                
                // 更新顺序列表
                updateSequenceList();
            }
            
            // 更新顺序列表
            function updateSequenceList() {
                sequenceList.innerHTML = markedSequence.length > 0 ? 
                    markedSequence.map((name, index) => 
                        `<div class="sequence-item" data-name="${name}">${index + 1}. ${name}</div>`
                    ).join('') : 
                    '<div>暂无批改记录</div>';
                
                // 添加点击事件到顺序列表项
                document.querySelectorAll('.sequence-item').forEach(item => {
                    item.addEventListener('click', function() {
                        const name = this.dataset.name;
                        // 从已批改列表中移除
                        markedStudents = markedStudents.filter(n => n !== name);
                        markedSequence = markedSequence.filter(n => n !== name);
                        
                        // 更新本地存储
                        localStorage.setItem('markedStudents', JSON.stringify(markedStudents));
                        localStorage.setItem('markedSequence', JSON.stringify(markedSequence));
                        
                        // 重新显示该学生
                        const studentItem = document.querySelector(`.student-item[data-name="${name}"]`);
                        if (studentItem) {
                            studentItem.style.display = '';
                        }
                        
                        // 更新显示
                        updateDisplay();
                    });
                });
            }
            
            // 更新分组计数
            function updateGroupCounts() {
                document.querySelectorAll('.student-group').forEach(group => {
                    const visibleCount = group.querySelectorAll('.student-list .student-item[style=""]').length;
                    group.querySelector('.group-title').dataset.count = visibleCount;
                });
            }
            
            // 搜索功能
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                
                studentItems.forEach(item => {
                    if (markedStudents.includes(item.dataset.name)) {
                        return; // 已批改的学生不参与搜索
                    }
                    
                    const name = item.dataset.name.toLowerCase();
                    const pinyin = item.dataset.pinyin.toLowerCase();
                    const isMatch = name.includes(searchTerm) || pinyin.includes(searchTerm);
                    
                    item.style.display = isMatch ? '' : 'none';
                });
                
                updateGroupCounts();
            });
            
            // 重置批改状态
            resetMarkedButton.addEventListener('click', function() {
                markedStudents = [];
                markedSequence = [];
                localStorage.removeItem('markedStudents');
                localStorage.removeItem('markedSequence');
                updateDisplay();
            });
            
            // 导出顺序
            exportButton.addEventListener('click', function() {
                if (markedSequence.length === 0) {
                    alert('没有可导出的批改顺序');
                    return;
                }
                
                const csvContent = "data:text/csv;charset=utf-8," 
                    + "序号,姓名\n" 
                    + markedSequence.map((name, index) => `${index + 1},${name}`).join("\n");
                
                const encodedUri = encodeURI(csvContent);
                const link = document.createElement("a");
                link.setAttribute("href", encodedUri);
                link.setAttribute("download", "批改顺序.csv");
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });
            
            // 题目编辑功能
            const editQuestionBtn = document.getElementById('editQuestionBtn');
            if (editQuestionBtn) {
                editQuestionBtn.addEventListener('click', function() {
                    const questionCard = this.closest('.question');
                    const questionId = questionCard.dataset.questionId;
                    const scrollPosition = window.scrollY;
                    
                    // 获取题目数据
                    fetch(`api.php?action=get_question&question_id=${questionId}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                enableEditMode(questionCard, data.data, scrollPosition);
                            } else {
                                alert('获取题目数据失败: ' + (data.message || '未知错误'));
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('获取题目数据失败: ' + error.message);
                        });
                });
            }
            
            // 启用编辑模式
            function enableEditMode(questionCard, question, scrollPosition) {
                questionCard.classList.add('edit-mode');
                
                const header = questionCard.querySelector('.question-meta');
                const difficultySpan = questionCard.querySelector('.difficulty');
                const topicSpan = questionCard.querySelector('.topic');
                const questionText = questionCard.querySelector('.question-text .html-content');
                const answerText = questionCard.querySelector('.answer-content .html-content');
                const questionImage = questionCard.querySelector('.question-content img');
                const editBtn = questionCard.querySelector('#editQuestionBtn');
                
                // 创建难度选择下拉框
                const difficultySelect = document.createElement('select');
                difficultySelect.innerHTML = `
                    <option value="easy" ${question.difficulty_level === 'easy' ? 'selected' : ''}>简单</option>
                    <option value="medium" ${question.difficulty_level === 'medium' ? 'selected' : ''}>中等</option>
                `;
                difficultySelect.style.padding = '8px';
                difficultySelect.style.borderRadius = '4px';
                
                // 创建主题输入框
                const topicInput = document.createElement('input');
                topicInput.type = 'text';
                topicInput.value = question.topic || '';
                topicInput.style.padding = '8px';
                topicInput.style.width = '200px';
                topicInput.style.borderRadius = '4px';
                topicInput.style.border = '1px solid #ddd';
                
                // 创建可编辑的题目内容区域
                const editableQuestion = document.createElement('div');
                editableQuestion.className = 'editable-content';
                editableQuestion.contentEditable = true;
                editableQuestion.innerHTML = question.question_text;
                
                // 创建题目内容工具栏
                const questionToolbar = createToolbar(editableQuestion, 'question');
                
                // 创建可编辑的答案内容区域
                const editableAnswer = document.createElement('div');
                editableAnswer.className = 'editable-content';
                editableAnswer.contentEditable = true;
                editableAnswer.innerHTML = question.answer_text;
                
                // 创建答案内容工具栏
                const answerToolbar = createToolbar(editableAnswer, 'answer');
                
                // 创建图片上传区域
                const imageUploadContainer = document.createElement('div');
                imageUploadContainer.className = 'image-upload-container';
                
                const imageUploadLabel = document.createElement('label');
                imageUploadLabel.className = 'image-upload-label';
                imageUploadLabel.textContent = '题目图片:';
                
                const imageUploadInput = document.createElement('input');
                imageUploadInput.type = 'file';
                imageUploadInput.accept = 'image/*';
                imageUploadInput.style.display = 'block';
                imageUploadInput.style.marginBottom = '10px';
                
                const imagePreview = document.createElement('img');
                imagePreview.className = 'image-preview';
                
                const removeImageBtn = document.createElement('span');
                removeImageBtn.className = 'remove-image';
                removeImageBtn.textContent = '移除图片';
                removeImageBtn.style.display = 'none';
                
                // 如果有现有图片，显示预览
                if (questionImage && questionImage.src) {
                    imagePreview.src = questionImage.src;
                    imagePreview.style.display = 'block';
                    removeImageBtn.style.display = 'inline';
                }
                
                // 图片上传处理
                imageUploadInput.addEventListener('change', function(e) {
                    const file = e.target.files[0];
                    if (!file) return;
                    
                    if (!file.type.match('image.*')) {
                        alert('请选择图片文件');
                        return;
                    }
                    
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        imagePreview.src = event.target.result;
                        imagePreview.style.display = 'block';
                        removeImageBtn.style.display = 'inline';
                    };
                    reader.readAsDataURL(file);
                });
                
                // 移除图片处理
                removeImageBtn.addEventListener('click', function() {
                    imagePreview.src = '';
                    imagePreview.style.display = 'none';
                    this.style.display = 'none';
                    imageUploadInput.value = '';
                });
                
                imageUploadContainer.appendChild(imageUploadLabel);
                imageUploadContainer.appendChild(imageUploadInput);
                imageUploadContainer.appendChild(imagePreview);
                imageUploadContainer.appendChild(removeImageBtn);
                
                // 替换原有内容为可编辑版本
                difficultySpan.replaceWith(difficultySelect);
                topicSpan.replaceWith(topicInput);
                
                // 插入题目工具栏和可编辑区域
                questionText.parentNode.insertBefore(questionToolbar, questionText);
                questionText.replaceWith(editableQuestion);
                
                // 插入图片上传区域
                if (questionImage) {
                    questionImage.replaceWith(imageUploadContainer);
                } else {
                    editableQuestion.parentNode.insertBefore(imageUploadContainer, editableQuestion.nextSibling);
                }
                
                // 插入答案工具栏和可编辑区域
                answerText.parentNode.insertBefore(answerToolbar, answerText);
                answerText.replaceWith(editableAnswer);
                
                // 创建保存和取消按钮
                const saveBtn = document.createElement('button');
                saveBtn.className = 'edit-btn save-btn';
                saveBtn.textContent = '保存';
                saveBtn.style.marginLeft = '10px';
                
                const cancelBtn = document.createElement('button');
                cancelBtn.className = 'edit-btn cancel-btn';
                cancelBtn.textContent = '取消';
                cancelBtn.style.marginLeft = '10px';
                
                // 移除编辑按钮
                if (editBtn) editBtn.remove();
                
                // 创建编辑控制区域
                const editControls = document.createElement('div');
                editControls.className = 'edit-controls';
                editControls.appendChild(saveBtn);
                editControls.appendChild(cancelBtn);
                
                header.appendChild(editControls);
                
                // 保存按钮点击事件
                saveBtn.addEventListener('click', async function() {
                    const updatedData = {
                        difficulty: difficultySelect.value,
                        topic: topicInput.value,
                        question_text: editableQuestion.innerHTML,
                        answer_text: editableAnswer.innerHTML
                    };
                    
                    // 处理图片上传
                    if (imageUploadInput.files.length > 0) {
                        const formData = new FormData();
                        formData.append('image', imageUploadInput.files[0]);
                        formData.append('question_id', question.question_id);
                        
                        try {
                            const uploadResponse = await fetch('upload_question_image.php', {
                                method: 'POST',
                                body: formData
                            });
                            
                            const uploadData = await uploadResponse.json();
                            
                            if (!uploadData.success) {
                                throw new Error(uploadData.message || "图片上传失败");
                            }
                            
                            updatedData.question_image = uploadData.image_path;
                        } catch (error) {
                            console.error('图片上传失败:', error);
                            alert(`图片上传失败: ${error.message}`);
                            return;
                        }
                    } else if (imagePreview.style.display === 'none' && question.question_image) {
                        // 如果图片被移除
                        updatedData.question_image = '';
                    }
                    
                    try {
                        const response = await fetch('api.php', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded',
                            },
                            body: new URLSearchParams({
                                action: 'update_question',
                                question_id: question.question_id,
                                difficulty: updatedData.difficulty,
                                topic: updatedData.topic,
                                question_text: updatedData.question_text,
                                answer_text: updatedData.answer_text,
                                question_image: updatedData.question_image || ''
                            })
                        });
                        
                        if (!response.ok) {
                            throw new Error(`服务器返回错误: ${response.status}`);
                        }
                        
                        const data = await response.json();
                        
                        if (!data.success) {
                            throw new Error(data.message || "更新题目失败");
                        }
                        
                        // 重新加载页面以显示更新后的内容
                        window.location.reload();
                        
                    } catch (error) {
                        console.error('更新题目失败:', error);
                        alert(`更新题目失败: ${error.message}`);
                    }
                });
                
                // 取消按钮点击事件
                cancelBtn.addEventListener('click', function() {
                    questionCard.classList.remove('edit-mode');
                    window.location.reload();
                });
            }
            
            // 创建格式化工具栏
            function createToolbar(editableElement, type) {
                const toolbar = document.createElement('div');
                toolbar.className = 'toolbar';
                
                // 添加HTML查看/编辑切换按钮
                const toggleHtmlBtn = document.createElement('button');
                toggleHtmlBtn.textContent = '查看HTML';
                toggleHtmlBtn.title = '切换查看HTML源代码';
                
                // 格式按钮点击处理函数
                const handleFormatButtonClick = (tag) => {
                    const isHtmlMode = editableElement.getAttribute('data-html-mode') === 'true';
                    
                    if (isHtmlMode) {
                        // HTML模式下的处理
                        const textarea = editableElement.querySelector('textarea');
                        const startPos = textarea.selectionStart;
                        const endPos = textarea.selectionEnd;
                        
                        // 定义要插入的内容
                        let insertContent = '';
                        if (tag === 'table') {
                            // 表格特殊处理 - 插入两行两列的表格
                            insertContent = 
                                '<table>\n' +
                                '  <tr>\n' +
                                '    <td>第1行第1列</td>\n' +
                                '    <td>第1行第2列</td>\n' +
                                '  </tr>\n' +
                                '  <tr>\n' +
                                '    <td>第2行第1列</td>\n' +
                                '    <td>第2行第1列</td>\n' +
                                '  </tr>\n' +
                                '</table>';
                        } else if (tag === 'ul') {
                            // 列表特殊处理
                            insertContent = '<ul>\n  <li>列表项1</li>\n  <li>列表项2</li>\n</ul>';
                        } else if (tag === 'br') {
                            insertContent = '<br>';
                        } else {
                            const selectedText = textarea.value.substring(startPos, endPos);
                            insertContent = `<${tag}>${selectedText || ''}</${tag}>`;
                        }
                        
                        // 插入内容到textarea
                        const beforeText = textarea.value.substring(0, startPos);
                        const afterText = textarea.value.substring(endPos);
                        textarea.value = beforeText + insertContent + afterText;
                        
                        // 设置光标位置
                        setTimeout(() => {
                            if (tag === 'table' || tag === 'ul') {
                                // 对于表格和列表，将光标放在第一个可编辑位置
                                const contentPos = beforeText.length + insertContent.indexOf('内容');
                                textarea.selectionStart = contentPos;
                                textarea.selectionEnd = contentPos + 2; // 选中"内容"二字
                            } else {
                                // 其他标签，将光标放在标签中间
                                const cursorPos = beforeText.length + insertContent.length;
                                if (insertContent.endsWith(`</${tag}>`)) {
                                    textarea.selectionStart = beforeText.length + `<${tag}>`.length;
                                    textarea.selectionEnd = textarea.selectionStart;
                                } else {
                                    textarea.selectionStart = cursorPos;
                                    textarea.selectionEnd = cursorPos;
                                }
                            }
                            textarea.focus();
                        }, 0);
                    } else {
                        // 正常模式下的处理
                        const selection = window.getSelection();
                        if (!selection.rangeCount) return;
                        
                        const range = selection.getRangeAt(0);
                        const selectedText = range.toString();
                        
                        // 检查选中文本是否已经在对应的标签内
                        let parent = range.commonAncestorContainer;
                        while (parent && parent !== editableElement) {
                            if (parent.nodeName === tag.toUpperCase()) {
                                // 如果已经在对应的标签内，则取消格式
                                const textNode = document.createTextNode(parent.textContent);
                                parent.parentNode.replaceChild(textNode, parent);
                                return;
                            }
                            parent = parent.parentNode;
                        }
                        
                        let newContent = '';
                        switch (tag) {
                            case 'table':
                                newContent = `<table><tr><td>内容</td><td>内容</td></tr><tr><td>内容</td><td>内容</td></tr></table>`;
                                break;
                            case 'ul':
                                newContent = `<ul><li>列表项</li><li>列表项</li></ul>`;
                                break;
                            case 'br':
                                newContent = `<br>`;
                                break;
                            default:
                                newContent = `<${tag}>${selectedText}</${tag}>`;
                        }
                        
                        // 如果选择了文本，替换选择的内容
                        if (selectedText) {
                            range.deleteContents();
                            range.insertNode(document.createRange().createContextualFragment(newContent));
                        } else {
                            // 如果没有选择文本，在光标位置插入新内容
                            range.insertNode(document.createRange().createContextualFragment(newContent));
                        }
                        
                        // 恢复焦点到可编辑区域
                        editableElement.focus();
                    }
                };
                
                toggleHtmlBtn.addEventListener('click', function() {
                    const isHtmlMode = editableElement.getAttribute('data-html-mode') === 'true';
                    
                    if (isHtmlMode) {
                        // 从HTML模式切换回正常模式
                        const textarea = editableElement.querySelector('textarea');
                        const htmlContent = textarea.value;
                        
                        // 恢复为可编辑区域并设置内容
                        editableElement.innerHTML = htmlContent;
                        editableElement.contentEditable = true;
                        editableElement.removeAttribute('data-html-mode');
                        toggleHtmlBtn.textContent = '查看HTML';
                    } else {
                        // 保存当前HTML内容
                        const htmlContent = editableElement.innerHTML;
                        editableElement.setAttribute('data-original-html', htmlContent);
                        
                        // 创建textarea显示HTML源代码
                        const textarea = document.createElement('textarea');
                        textarea.value = htmlContent;
                        textarea.style.width = '100%';
                        textarea.style.minHeight = '150px';
                        textarea.style.padding = '10px';
                        textarea.style.fontFamily = 'monospace';
                        textarea.style.whiteSpace = 'pre';
                        
                        // 替换可编辑区域为textarea
                        editableElement.innerHTML = '';
                        editableElement.appendChild(textarea);
                        editableElement.contentEditable = false;
                        editableElement.setAttribute('data-html-mode', 'true');
                        toggleHtmlBtn.textContent = '返回编辑';
                    }
                });
                
                // 将HTML切换按钮放在最后
                toolbar.appendChild(toggleHtmlBtn);
                
                const addButton = (text, tag, icon = null) => {
                    const btn = document.createElement('button');
                    btn.title = text;
                    
                    if (icon) {
                        btn.innerHTML = icon;
                    } else {
                        btn.textContent = text;
                    }
                    
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        handleFormatButtonClick(tag);
                    });
                    
                    // 将格式按钮插入到HTML切换按钮之前
                    toolbar.insertBefore(btn, toggleHtmlBtn);
                    return btn;
                };
                
                addButton('B', 'b');
                addButton('上标', 'sup');
                addButton('下标', 'sub');
                addButton('列表', 'ul');
                addButton('表格', 'table');
                addButton('换行', 'br', '↵');
                
                const separator = document.createElement('div');
                separator.className = 'toolbar-separator';
                toolbar.insertBefore(separator, toggleHtmlBtn);
                
                const tip = document.createElement('small');
                tip.textContent = '选中文字后点击按钮添加格式';
                toolbar.insertBefore(tip, toggleHtmlBtn);
                
                return toolbar;
            }
            
            // 初始显示
            updateDisplay();
        });
async function saveQuestionChanges(questionId, updatedData) {
    try {
        const response = await fetch('api.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                action: 'update_question',
                question_id: questionId,
                difficulty: updatedData.difficulty,
                topic: updatedData.topic,
                question_text: updatedData.question_text,
                answer_text: updatedData.answer_text
            })
        });

        if (!response.ok) {
            throw new Error(`服务器返回错误: ${response.status}`);
        }

        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || "更新题目失败");
        }

        return data;
    } catch (error) {
        console.error('更新题目失败:', error);
        throw error;
    }
}

// 添加复制功能按钮
function addCopyButtons() {
    const questionCards = document.querySelectorAll('.question-card');
    
    questionCards.forEach(card => {
        const header = card.querySelector('.question-header');
        if (!header) return;
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i> 复制';
        copyBtn.title = '复制题目内容';
        copyBtn.style.marginLeft = '10px';
        copyBtn.style.padding = '6px 12px';
        copyBtn.style.backgroundColor = '#2196F3';
        copyBtn.style.color = 'white';
        copyBtn.style.border = 'none';
        copyBtn.style.borderRadius = '4px';
        copyBtn.style.cursor = 'pointer';
        
        copyBtn.addEventListener('click', () => {
            const questionText = card.querySelector('.question-text .html-content').innerHTML;
            const answerText = card.querySelector('.answer-content .html-content').innerHTML;
            
            const contentToCopy = `题目:\n${questionText}\n\n答案:\n${answerText}`;
            
            navigator.clipboard.writeText(contentToCopy)
                .then(() => {
                    showToast('题目已复制到剪贴板');
                })
                .catch(err => {
                    console.error('复制失败:', err);
                    showToast('复制失败，请手动复制');
                });
        });
        
        header.appendChild(copyBtn);
    });
}

// 显示Toast通知
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// 添加样式到head
const style = document.createElement('style');
style.textContent = `
    .toast-notification {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #333;
        color: white;
        padding: 12px 24px;
        border-radius: 4px;
        z-index: 1000;
        opacity: 0.9;
        transition: opacity 0.3s;
    }
    
    .toast-notification.fade-out {
        opacity: 0;
    }
    
    .copy-btn {
        transition: all 0.2s;
    }
    
    .copy-btn:hover {
        background-color: #0b7dda !important;
        transform: translateY(-1px);
    }
    
    .copy-btn:active {
        transform: translateY(0);
    }
    
    .edit-btn {
        transition: all 0.2s;
    }
    
    .edit-btn:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    
    .edit-btn:active {
        transform: translateY(0);
    }
    
    .toolbar button {
        transition: all 0.2s;
    }
    
    .toolbar button:hover {
        transform: translateY(-1px);
    }
    
    .toolbar button:active {
        transform: translateY(0);
    }
`;
document.head.appendChild(style);

// 初始化复制按钮
addCopyButtons();

// 添加Font Awesome图标库
const faLink = document.createElement('link');
faLink.rel = 'stylesheet';
faLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
document.head.appendChild(faLink);
    </script>
</body>
</html>