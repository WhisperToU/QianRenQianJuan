<?php
//version3才会需要，version3添加了学生反馈功能。
require_once 'config.php';

header('Content-Type: application/json');

$response = ['success' => false];

try {
    $studentId = isset($_POST['student_id']) ? (int)$_POST['student_id'] : null;
    $questionId = isset($_POST['question_id']) ? (int)$_POST['question_id'] : null;
    $score = isset($_POST['performance_score']) ? $_POST['performance_score'] : null;
    $feedback = isset($_POST['student_feedback']) ? $_POST['student_feedback'] : null;
    $date = isset($_POST['date']) ? $_POST['date'] : date('Y-m-d');
    $recordId = isset($_POST['record_id']) ? (int)$_POST['record_id'] : null;

    if (!$studentId || !$questionId) {
        throw new Exception('缺少学生ID或题目ID');
    }

    if ($recordId) {
        // 更新现有记录
        $stmt = $conn->prepare("
            UPDATE student_records 
            SET performance_score = ?, student_feedback = ?
            WHERE record_id = ?
        ");
        $stmt->bind_param('ssi', $score, $feedback, $recordId);
    } else {
        // 创建新记录
        $stmt = $conn->prepare("
            INSERT INTO student_records 
            (student_id, question_id, performance_score, student_feedback, create_at)
            VALUES (?, ?, ?, ?, ?)
        ");
        $stmt->bind_param('iisss', $studentId, $questionId, $score, $feedback, $date);
    }

    if ($stmt->execute()) {
        $response['success'] = true;
    } else {
        throw new Exception('数据库操作失败: ' . $stmt->error);
    }

    $stmt->close();
} catch (Exception $e) {
    $response['message'] = $e->getMessage();
}

echo json_encode($response);
?>