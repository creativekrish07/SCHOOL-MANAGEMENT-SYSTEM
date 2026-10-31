drop database main;

-- 1. Create and Select the Database
CREATE DATABASE IF NOT EXISTS main1;
USE main1;

-- 2. Create 'class' Table first (referenced by studentrec and attendance)
CREATE TABLE class (
  class_id varchar(50) NOT NULL,
  grade int DEFAULT NULL,
  section char(1) DEFAULT NULL,
  PRIMARY KEY (class_id)
);

-- 3. Create 'studentrec' Table (referenced by attendance)
CREATE TABLE studentrec (
  student_id int NOT NULL AUTO_INCREMENT,
  name varchar(255) DEFAULT NULL,
  class int DEFAULT NULL,
  section char(1) DEFAULT NULL,
  class_id varchar(50) DEFAULT NULL,
  phone_number varchar(20) DEFAULT NULL,
  email varchar(255) DEFAULT NULL,
  date_of_birth date DEFAULT NULL,
  PRIMARY KEY (student_id),
  KEY class_id (class_id),
  CONSTRAINT studentrec_ibfk_1 FOREIGN KEY (class_id) REFERENCES class (class_id)
);

-- 4. Create 'attendance' Table (links students and classes)
CREATE TABLE attendance (
  attendance_id int NOT NULL AUTO_INCREMENT,
  student_id int DEFAULT NULL,
  class_id varchar(50) DEFAULT NULL,
  date date DEFAULT NULL,
  status varchar(10) DEFAULT NULL,
  PRIMARY KEY (attendance_id),
  KEY student_id (student_id),
  KEY class_id (class_id),
  CONSTRAINT attendance_ibfk_1 FOREIGN KEY (student_id) REFERENCES studentrec (student_id),
  CONSTRAINT attendance_ibfk_2 FOREIGN KEY (class_id) REFERENCES class (class_id)
);

-- 5. Create 'login' Table
CREATE TABLE login (
  userid int NOT NULL,
  password varchar(64) NOT NULL,
  role varchar(50) DEFAULT NULL,
  PRIMARY KEY (userid)
);

-- 6. Create 'circulars' Table
CREATE TABLE circulars (
  circular_id int NOT NULL AUTO_INCREMENT,
  circular_title varchar(255) NOT NULL,
  circular_link varchar(5120) DEFAULT NULL,
  grade int NOT NULL,
  date_posted timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (circular_id)
);

-- 7. Create 'qp' (Question Paper) Table
CREATE TABLE qp (
  qp_id int NOT NULL AUTO_INCREMENT,
  qp_link varchar(5000) NOT NULL,
  qp_type varchar(50) NOT NULL,
  subject varchar(100) NOT NULL,
  grade int NOT NULL,
  max_marks int NOT NULL,
  answer_key_link varchar(5000) DEFAULT NULL,
  uploaded_on datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (qp_id)
);

-- 8. (Optional) Create a default Admin user so you can log in immediately
-- User ID: 1001, Password: 'password' (Change 'password' to what you use in your python code)
INSERT INTO login (userid, password, role) VALUES (12345, 12345, 'admin');




