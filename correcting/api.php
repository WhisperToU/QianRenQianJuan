<?php
require_once 'config.php';

header('Content-Type: application/json');

$action = $_GET['action'] ?? $_POST['action'] ?? '';

try {
    switch ($action) {
        case 'get_question':
            $questionId = $_GET['question_id'] ?? 0;
            $stmt = $conn->prepare("SELECT * FROM questions WHERE question_id = ?");
            $stmt->bind_param('i', $questionId);
            $stmt->execute();
            $result = $stmt->get_result();
            
            if ($result->num_rows > 0) {
                $question = $result->fetch_assoc();
                echo json_encode(['success' => true, 'data' => $question]);
            } else {
                echo json_encode(['success' => false, 'message' => '题目不存在']);
            }
            break;
            
        case 'update_question':
            $questionId = $_POST['question_id'] ?? 0;
            $difficulty = $_POST['difficulty'] ?? '';
            $topic = $_POST['topic'] ?? '';
            $questionText = $_POST['question_text'] ?? '';
            $answerText = $_POST['answer_text'] ?? '';
            
            $stmt = $conn->prepare("UPDATE questions SET 
                difficulty_level = ?, 
                topic = ?, 
                question_text = ?, 
                answer_text = ? 
                WHERE question_id = ?");
            $stmt->bind_param('ssssi', $difficulty, $topic, $questionText, $answerText, $questionId);
            $stmt->execute();
            
            if ($stmt->affected_rows > 0) {
                echo json_encode(['success' => true]);
            } else {
                echo json_encode(['success' => false, 'message' => '更新失败或数据未更改']);
            }
            break;
            
        default:
            echo json_encode(['success' => false, 'message' => '无效的操作']);
    }
} catch (Exception $e) {
    echo json_encode(['success' => false, 'message' => '服务器错误: ' . $e->getMessage()]);
}

$conn->close();
?>