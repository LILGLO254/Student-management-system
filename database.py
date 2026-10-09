from mysql.connector import connect, Error


def create_connection():
    connection = None
    cursor = None

    try:
        connection = connect(
            host="localhost",
            user="root",
            password="gloria2005",
            database="STUDENT_MANAGEMENT_SYSTEM",
            charset="utf8",
        )
        cursor = connection.cursor()

        table_statements = (
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(150) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role ENUM ("student","lecturer", "admin") NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS departments (
                department_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL UNIQUE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS programs (
                program_id INT AUTO_INCREMENT PRIMARY KEY,
                department_id INT NOT NULL,
                name VARCHAR(150) NOT NULL,
                duration INT,
                FOREIGN KEY (department_id)
                    REFERENCES departments(department_id)
                    ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS students (
                user_id INT NOT NULL,
                student_id INT AUTO_INCREMENT UNIQUE PRIMARY KEY,
                admission_no VARCHAR(50) NOT NULL UNIQUE,
                names VARCHAR(150) NOT NULL,
                gender ENUM ("Male", "Female"),
                date_of_birth DATE,
                phone VARCHAR(30),
                email VARCHAR(150),
                program_id INT,
                FOREIGN KEY (program_id)
                    REFERENCES programs(program_id)
                    ON DELETE SET NULL,
                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE

            )
            """,
            """
            CREATE TABLE IF NOT EXISTS lecturers (
                lecturer_id INT AUTO_INCREMENT PRIMARY KEY,
                staff_no VARCHAR(50) NOT NULL UNIQUE,
                name VARCHAR(150) NOT NULL,
                email VARCHAR(150),
                department_id INT,
                FOREIGN KEY (department_id)
                    REFERENCES departments(department_id)
                    ON DELETE SET NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS semesters (
                semester_id INT AUTO_INCREMENT PRIMARY KEY,
                academic_year VARCHAR(20) NOT NULL,
                name VARCHAR(50) NOT NULL,
                start_date DATE,
                end_date DATE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_id INT AUTO_INCREMENT PRIMARY KEY,
                course_code VARCHAR(50) NOT NULL UNIQUE,
                course_name VARCHAR(150) NOT NULL,
                department_id INT,
                credits INT,
                FOREIGN KEY (department_id)
                    REFERENCES departments(department_id)
                    ON DELETE SET NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                course_id INT NOT NULL,
                semester_id INT NOT NULL,
                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (course_id)
                    REFERENCES courses(course_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (semester_id)
                    REFERENCES semesters(semester_id)
                    ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS assessments (
                assessment_id INT AUTO_INCREMENT PRIMARY KEY,
                course_id INT NOT NULL,
                type VARCHAR(50) NOT NULL,
                title VARCHAR(150) NOT NULL,
                total_marks DECIMAL(5,2),
                date DATE,
                FOREIGN KEY (course_id)
                    REFERENCES courses(course_id)
                    ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS grades (
                grade_id INT AUTO_INCREMENT PRIMARY KEY,
                assessment_id INT NOT NULL,
                student_id INT NOT NULL,
                marks DECIMAL(5,2),
                grade VARCHAR(5),
                FOREIGN KEY (assessment_id)
                    REFERENCES assessments(assessment_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                course_id INT NOT NULL,
                date DATE NOT NULL,
                status ENUM('Present', 'Absent') NOT NULL,
                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (course_id)
                    REFERENCES courses(course_id)
                    ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS fees (
                fee_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                type VARCHAR(100),
                due_date DATE,
                status VARCHAR(30),
                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                method VARCHAR(50),
                reference VARCHAR(100),
                payment_date DATE,
                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS timetable (
                timetable_id INT AUTO_INCREMENT PRIMARY KEY,
                course_id INT NOT NULL,
                lecturer_id INT,
                room VARCHAR(100),
                day VARCHAR(20),
                start_time TIME,
                end_time TIME,
                FOREIGN KEY (course_id)
                    REFERENCES courses(course_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (lecturer_id)
                    REFERENCES lecturers(lecturer_id)
                    ON DELETE SET NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS assignments (
                assignment_id INT AUTO_INCREMENT PRIMARY KEY,
                course_id INT NOT NULL,
                title VARCHAR(150) NOT NULL,
                description TEXT,
                deadline DATETIME,
                FOREIGN KEY (course_id)
                    REFERENCES courses(course_id)
                    ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS submissions (
                submission_id INT AUTO_INCREMENT PRIMARY KEY,
                assignment_id INT NOT NULL,
                student_id INT NOT NULL,
                file_path VARCHAR(255),
                submitted_at DATETIME,
                mark DECIMAL(5,2),
                FOREIGN KEY (assignment_id)
                    REFERENCES assignments(assignment_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS announcements (
                announcement_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                target_role VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                action VARCHAR(150),
                entity VARCHAR(100),
                entity_id INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
            )
            """,
        )

        for statement in table_statements:
            cursor.execute(statement)

        cursor.execute(
            "SELECT COLUMN_NAME, CHARACTER_MAXIMUM_LENGTH "
            "FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' "
            "AND COLUMN_NAME IN ('username', 'email', 'password')"
        )
        user_column_lengths = dict(cursor.fetchall())
        if any(
            user_column_lengths.get(column, 0) < required_length
            for column, required_length in (
                ("username", 100),
                ("email", 150),
                ("password", 255),
            )
        ):
            cursor.execute(
                "ALTER TABLE users "
                "MODIFY COLUMN username VARCHAR(100) NOT NULL, "
                "MODIFY COLUMN email VARCHAR(150) NOT NULL, "
                "MODIFY COLUMN password VARCHAR(255) NOT NULL"
            )

        connection.commit()
        print("All tables created successfully!")
        return connection
    except Error as error:
        print("Database error:", error)
        if connection is not None and connection.is_connected():
            connection.close()
        return None
    finally:
        if cursor is not None:
            cursor.close()
