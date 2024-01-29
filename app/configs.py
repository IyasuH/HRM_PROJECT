import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("DB_HOST")
MYSQL_USER = os.getenv("DB_USER")
MYSQL_PASSWORD = os.getenv("DB_PASSWORD")
MYSQL_DB = os.getenv("DB_DB")

def connect():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )

conn = connect()

# conn = mysql.connector.connect(
# )

cursor = conn.cursor()

table_creates = (
    """
        CREATE TABLE IF NOT EXISTS admin(
            admin_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS manager(
            manager_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS employee(
            employee_id INT AUTO_INCREMENT PRIMARY KEY,
            manager_id INT NOT NULL,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            first_name  VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            date_of_birth DATE NOT NULL,
            gender ENUM('M', 'F') NOT NULL,
            address VARCHAR(255),
            contact_number VARCHAR(255),
            hire_date DATE NOT NULL,
            dept VARCHAR(255) NOT NULL,
            role VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (manager_id) REFERENCES manager(manager_id)
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS project(
            project_id INT AUTO_INCREMENT PRIMARY KEY,
            manager_id INT NOT NULL,
            project_name VARCHAR(255) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (manager_id) REFERENCES manager(manager_id)
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS leave_tbl(
            leave_id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id INT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            leave_type VARCHAR(255) NOT NULL,
            status VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS salary(
            salary_id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id INT NOT NULL,
            salary_date DATE NOT NULL,
            amount FLOAT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
        )
    """
)

for tbl_create in table_creates:
    cursor.execute(tbl_create)

conn.commit()

cursor.close()
# conn.close()