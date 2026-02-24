-- ============================================
-- ACADEMIC ERP SYSTEM - COMPLETE MYSQL SCHEMA
-- RAG Tutor Database
-- ============================================

CREATE DATABASE IF NOT EXISTS rag_tutor;
USE rag_tutor;

-- ==========================================
-- CORE TABLES
-- ==========================================

-- Users table (all roles)
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'student', 'teacher') NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    profile_picture VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- Degrees (e.g., B.Tech, M.Tech, BCA, MCA)
CREATE TABLE IF NOT EXISTS degrees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    duration_years INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Departments (e.g., Computer Science, Electronics)
CREATE TABLE IF NOT EXISTS departments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Semesters
CREATE TABLE IF NOT EXISTS semesters (
    id INT PRIMARY KEY AUTO_INCREMENT,
    number INT NOT NULL,
    degree_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (degree_id) REFERENCES degrees(id) ON DELETE CASCADE,
    UNIQUE KEY unique_sem_degree (number, degree_id)
);

-- Subjects
CREATE TABLE IF NOT EXISTS subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    credits INT DEFAULT 3,
    degree_id INT NOT NULL,
    department_id INT NOT NULL,
    semester_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (degree_id) REFERENCES degrees(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (semester_id) REFERENCES semesters(id),
    INDEX idx_semester (semester_id)
);

-- ==========================================
-- STUDENT-SPECIFIC TABLES
-- ==========================================

-- Student profiles
CREATE TABLE IF NOT EXISTS student_profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    roll_number VARCHAR(50) UNIQUE NOT NULL,
    degree_id INT NOT NULL,
    department_id INT NOT NULL,
    current_semester_id INT NOT NULL,
    passout_year INT NOT NULL,
    admission_year INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (degree_id) REFERENCES degrees(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (current_semester_id) REFERENCES semesters(id),
    INDEX idx_roll (roll_number)
);

-- Student-Subject mapping (auto-assigned based on semester)
CREATE TABLE IF NOT EXISTS student_subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    semester_id INT NOT NULL,
    academic_year VARCHAR(9) NOT NULL,
    is_current BOOLEAN DEFAULT TRUE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (semester_id) REFERENCES semesters(id),
    UNIQUE KEY unique_student_subject (student_id, subject_id, academic_year)
);

-- Semester history (archived semesters)
CREATE TABLE IF NOT EXISTS semester_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    semester_id INT NOT NULL,
    academic_year VARCHAR(9) NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (semester_id) REFERENCES semesters(id)
);

-- ==========================================
-- TEACHER-SPECIFIC TABLES
-- ==========================================

-- Teacher profiles
CREATE TABLE IF NOT EXISTS teacher_profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    department_id INT NOT NULL,
    designation VARCHAR(100),
    joining_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Teacher-Subject assignments (by admin)
CREATE TABLE IF NOT EXISTS teacher_subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_id INT NOT NULL,
    subject_id INT NOT NULL,
    academic_year VARCHAR(9) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teacher_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    UNIQUE KEY unique_teacher_subject (teacher_id, subject_id, academic_year)
);

-- Class allocations (teacher to degree+department+semester)
CREATE TABLE IF NOT EXISTS class_allocations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_id INT NOT NULL,
    degree_id INT NOT NULL,
    department_id INT NOT NULL,
    semester_id INT NOT NULL,
    subject_id INT NOT NULL,
    academic_year VARCHAR(9) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (teacher_id) REFERENCES teacher_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (degree_id) REFERENCES degrees(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (semester_id) REFERENCES semesters(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- ==========================================
-- QUIZ MODULE
-- ==========================================

CREATE TABLE IF NOT EXISTS quizzes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subject_id INT NOT NULL,
    teacher_id INT NOT NULL,
    duration_minutes INT DEFAULT 30,
    total_marks INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    start_time DATETIME,
    end_time DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (teacher_id) REFERENCES teacher_profiles(id)
);

CREATE TABLE IF NOT EXISTS quiz_questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quiz_id INT NOT NULL,
    question_text TEXT NOT NULL,
    option_a VARCHAR(500) NOT NULL,
    option_b VARCHAR(500) NOT NULL,
    option_c VARCHAR(500) NOT NULL,
    option_d VARCHAR(500) NOT NULL,
    correct_option ENUM('A', 'B', 'C', 'D') NOT NULL,
    marks INT DEFAULT 1,
    explanation TEXT,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quiz_id INT NOT NULL,
    student_id INT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP NULL,
    score INT DEFAULT 0,
    total_questions INT NOT NULL,
    correct_answers INT DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id),
    FOREIGN KEY (student_id) REFERENCES student_profiles(id),
    UNIQUE KEY unique_attempt (quiz_id, student_id)
);

CREATE TABLE IF NOT EXISTS quiz_responses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    attempt_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_option ENUM('A', 'B', 'C', 'D'),
    is_correct BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (attempt_id) REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES quiz_questions(id)
);

-- ==========================================
-- ASSIGNMENT MODULE
-- ==========================================

CREATE TABLE IF NOT EXISTS assignments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subject_id INT NOT NULL,
    teacher_id INT NOT NULL,
    due_date DATETIME NOT NULL,
    max_marks INT DEFAULT 100,
    attachment_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (teacher_id) REFERENCES teacher_profiles(id)
);

CREATE TABLE IF NOT EXISTS assignment_submissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    assignment_id INT NOT NULL,
    student_id INT NOT NULL,
    submission_url VARCHAR(500) NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    marks_obtained INT,
    feedback TEXT,
    status ENUM('submitted', 'graded', 'late', 'resubmit') DEFAULT 'submitted',
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (student_id) REFERENCES student_profiles(id),
    UNIQUE KEY unique_submission (assignment_id, student_id)
);

-- ==========================================
-- CHAT MODULE
-- ==========================================

CREATE TABLE IF NOT EXISTS chat_conversations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    teacher_id INT NOT NULL,
    subject_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_profiles(id),
    FOREIGN KEY (teacher_id) REFERENCES teacher_profiles(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    UNIQUE KEY unique_conversation (student_id, teacher_id)
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    conversation_id INT NOT NULL,
    sender_id INT NOT NULL,
    sender_role ENUM('student', 'teacher') NOT NULL,
    message TEXT NOT NULL,
    is_urgent BOOLEAN DEFAULT FALSE,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES chat_conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    INDEX idx_conversation (conversation_id),
    INDEX idx_created (created_at)
);

-- ==========================================
-- AI TUTOR MODULE
-- ==========================================

-- PDF documents for RAG (files on disk, paths in MySQL)
CREATE TABLE IF NOT EXISTS pdf_documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT,
    uploaded_by INT NOT NULL,
    is_indexed BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    indexed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- AI chat sessions
CREATE TABLE IF NOT EXISTS ai_chat_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_profiles(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- AI chat messages
CREATE TABLE IF NOT EXISTS ai_chat_messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    role ENUM('user', 'assistant') NOT NULL,
    content TEXT NOT NULL,
    citations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES ai_chat_sessions(id) ON DELETE CASCADE
);

-- AI doubts tracking (for weak topic detection)
CREATE TABLE IF NOT EXISTS ai_doubt_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    topic VARCHAR(255),
    question TEXT NOT NULL,
    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_profiles(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    INDEX idx_student_subject (student_id, subject_id)
);

-- AI rate limiting
CREATE TABLE IF NOT EXISTS ai_rate_limits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    query_count INT DEFAULT 0,
    window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    UNIQUE KEY unique_student (student_id)
);

-- ==========================================
-- WEAK TOPIC DETECTION
-- ==========================================

CREATE TABLE IF NOT EXISTS weak_topics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    topic_name VARCHAR(255) NOT NULL,
    weakness_score DECIMAL(5,2) DEFAULT 0,
    source ENUM('quiz', 'ai_doubts', 'combined') NOT NULL,
    quiz_error_count INT DEFAULT 0,
    ai_doubt_count INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_profiles(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    UNIQUE KEY unique_weak_topic (student_id, subject_id, topic_name)
);

-- Class-level weak topics (aggregated for teachers)
CREATE TABLE IF NOT EXISTS class_weak_topics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    degree_id INT NOT NULL,
    department_id INT NOT NULL,
    semester_id INT NOT NULL,
    subject_id INT NOT NULL,
    topic_name VARCHAR(255) NOT NULL,
    affected_students INT DEFAULT 0,
    avg_weakness_score DECIMAL(5,2) DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (degree_id) REFERENCES degrees(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (semester_id) REFERENCES semesters(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- ==========================================
-- AUDIT LOGGING (Admin Safety)
-- ==========================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    entity VARCHAR(100) NOT NULL,
    entity_id INT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_entity (entity, entity_id),
    INDEX idx_user (user_id),
    INDEX idx_created (created_at)
);

-- ==========================================
-- SYSTEM SETTINGS (Exam Mode & Controls)
-- ==========================================

CREATE TABLE IF NOT EXISTS system_settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value VARCHAR(500) NOT NULL,
    description VARCHAR(255),
    updated_by INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Default settings
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('ai_tutor_enabled', 'true', 'Enable/disable AI Tutor globally'),
('ai_rate_limit_per_minute', '10', 'Max AI queries per student per minute'),
('exam_mode', 'false', 'When true, AI Tutor is disabled for academic integrity')
ON DUPLICATE KEY UPDATE setting_key = setting_key;

-- ==========================================
-- DEFAULT ADMIN USER
-- Password: Admin@123 (bcrypt hash)
-- ==========================================

INSERT INTO users (email, password_hash, role, full_name, is_active)
VALUES ('admin@college.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewofV5mNPd.W7iZu', 'admin', 'System Administrator', TRUE)
ON DUPLICATE KEY UPDATE email = email;

-- ==========================================
-- SAMPLE DATA (Optional)
-- ==========================================

-- Sample Degrees
INSERT INTO degrees (name, code, duration_years) VALUES
('Bachelor of Technology', 'BTECH', 4),
('Master of Technology', 'MTECH', 2),
('Bachelor of Computer Applications', 'BCA', 3),
('Master of Computer Applications', 'MCA', 2)
ON DUPLICATE KEY UPDATE name = name;

-- Sample Departments
INSERT INTO departments (name, code) VALUES
('Computer Science & Engineering', 'CSE'),
('Electronics & Communication', 'ECE'),
('Information Technology', 'IT'),
('Artificial Intelligence & ML', 'AIML')
ON DUPLICATE KEY UPDATE name = name;
