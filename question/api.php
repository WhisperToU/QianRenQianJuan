<?php 
require_once 'config.php'; 
 
// 设置响应头为JSON 
header('Content-Type: application/json');
 
try {
    // 获取数据库连接 
    $conn = getDBConnection();
    
    // 根据请求方法处理不同的操作 
    if ($_SERVER['REQUEST_METHOD'] === 'GET') {
        // 处理获取题目请求 
        handleGetQuestions($conn);
    } elseif ($_SERVER['REQUEST_METHOD'] === 'POST') {
        // 根据action参数决定操作 
        $action = $_POST['action'] ?? '';
        if ($action === 'add_question') {
            // 处理新增题目请求 
            handleAddQuestion($conn);
        } elseif ($action === 'update_question') {
            // 处理更新题目请求 
            handleUpdateQuestion($conn);
        } elseif ($action === 'delete_question') {
            // 处理删除题目请求 
            handleDeleteQuestion($conn);
        } else {
            throw new Exception("不支持的请求方法");
        }
    } else {
        throw new Exception("不支持的请求方法");
    }
    
} catch (Exception $e) {
    // 错误响应 
    echo json_encode([
        'success' => false,
        'message' => $e->getMessage()
    ]);
}
 
// 处理获取题目请求 
function handleGetQuestions($conn) {
    // 验证action参数 
    $action = $_GET['action'] ?? '';
    if ($action !== 'get_questions') {
        throw new Exception("无效的操作");
    }
    
    // 构建查询 
    $query = "SELECT * FROM questions";
    $conditions = [];
    $params = [];
    $types = '';
    
    // 添加筛选条件 
    if (!empty($_GET['difficulty'])) {
        $conditions[] = "difficulty_level = ?";
        $params[] = $_GET['difficulty'];
        $types .= 's';
    }
    
    if (!empty($_GET['topic'])) {
        $conditions[] = "topic LIKE ?";
        $params[] = '%'.$_GET['topic'].'%';
        $types .= 's';
    }
    
    // 组合完整SQL 
    if (!empty($conditions)) {
        $query .= " WHERE " . implode(" AND ", $conditions);
    }
    $query .= " ORDER BY created_at DESC";
    
    // 准备和执行查询 
    $stmt = $conn->prepare($query);
    if (!empty($params)) {
        $stmt->bind_param($types, ...$params);
    }
    $stmt->execute();
    $result = $stmt->get_result();
    
    // 获取数据 
    $questions = [];
    while ($row = $result->fetch_assoc()) {
        $questions[] = $row;
    }
    
    // 返回JSON响应 
    echo json_encode([
        'success' => true,
        'data' => $questions 
    ]);
}
 
// 处理新增题目请求 
function handleAddQuestion($conn) {
    // 验证action参数 
    $action = $_POST['action'] ?? '';
    if ($action !== 'add_question') {
        throw new Exception("无效的操作");
    }
    
    // 验证必填字段 
    $requiredFields = ['difficulty', 'topic'];
    foreach ($requiredFields as $field) {
        if (empty($_POST[$field])) {
            throw new Exception("缺少必填字段: " . $field);
        }
    }
    
    // 准备插入数据 
    $difficulty = $_POST['difficulty'];
    $topic = $_POST['topic'];
    $questionText = $_POST['question_text'] ?? '';
    $questionImage = $_POST['question_image'] ?? null;
    $answerText = $_POST['answer_text'] ?? '';
    
    // 准备SQL语句 
    $query = "INSERT INTO questions (difficulty_level, topic, question_text, question_image, answer_text, created_at) 
              VALUES (?, ?, ?, ?, ?, NOW())";
    
    $stmt = $conn->prepare($query);
    if ($questionImage) {
        $stmt->bind_param('sssss', $difficulty, $topic, $questionText, $questionImage, $answerText);
    } else {
        $stmt->bind_param('ssss', $difficulty, $topic, $questionText, $answerText);
        $questionImage = null;
    }
    
    // 执行插入 
    if ($stmt->execute()) {
        echo json_encode([
            'success' => true,
            'message' => '题目添加成功',
            'question_id' => $conn->insert_id 
        ]);
    } else {
        throw new Exception("添加题目失败: " . $conn->error);
    }
}
 
// 处理更新题目请求 
function handleUpdateQuestion($conn) {
    // 验证action参数 
    $action = $_POST['action'] ?? '';
    if ($action !== 'update_question') {
        throw new Exception("无效的操作");
    }
    
    // 验证必填字段 
    $requiredFields = ['question_id', 'difficulty', 'topic', 'question_text', 'answer_text'];
    foreach ($requiredFields as $field) {
        if (empty($_POST[$field])) {
            throw new Exception("缺少必填字段: " . $field);
        }
    }
    
    // 准备更新数据 
    $questionId = $_POST['question_id'];
    $difficulty = $_POST['difficulty'];
    $topic = $_POST['topic'];
    $questionText = $_POST['question_text'];
    $answerText = $_POST['answer_text'];
    
    // 准备SQL语句 
    $query = "UPDATE questions SET 
              difficulty_level = ?, 
              topic = ?, 
              question_text = ?, 
              answer_text = ? 
              WHERE question_id = ?";
    
    $stmt = $conn->prepare($query);
    $stmt->bind_param('ssssi', $difficulty, $topic, $questionText, $answerText, $questionId);
    
    // 执行更新 
    if ($stmt->execute()) {
        echo json_encode([
            'success' => true,
            'message' => '题目更新成功'
        ]);
    } else {
        throw new Exception("更新题目失败: " . $conn->error);
    }
}
 
// 处理删除题目请求 
function handleDeleteQuestion($conn) {
    // 验证action参数 
    $action = $_POST['action'] ?? '';
    if ($action !== 'delete_question') {
        throw new Exception("无效的操作");
    }
    
    // 验证必填字段 
    if (empty($_POST['question_id'])) {
        throw new Exception("缺少必填字段: question_id");
    }
    
    $questionId = $_POST['question_id'];
    
    // 准备SQL语句 
    $query = "DELETE FROM questions WHERE question_id = ?";
    $stmt = $conn->prepare($query);
    $stmt->bind_param('i', $questionId);
    
    // 执行删除 
    if ($stmt->execute()) {
        echo json_encode([
            'success' => true,
            'message' => '题目删除成功'
        ]);
    } else {
        throw new Exception("删除题目失败: " . $conn->error);
    }
}
?>