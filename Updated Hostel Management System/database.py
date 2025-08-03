import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self):
        self.db_path = 'data/hostel.db'
        self.init_db()

    def init_db(self):
        os.makedirs('data', exist_ok=True)
        os.makedirs('data/images', exist_ok=True)
        os.makedirs('data/id_cards', exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Drop table if exists for clean testing (remove in production)
        c.execute("DROP TABLE IF EXISTS students")

        c.execute('''CREATE TABLE IF NOT EXISTS students
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      registration_no TEXT UNIQUE NOT NULL,
                      first_name TEXT NOT NULL,
                      last_name TEXT NOT NULL,
                      father_name TEXT NOT NULL,
                      department TEXT NOT NULL,
                      room_no TEXT NOT NULL,
                      phone TEXT NOT NULL,
                      email TEXT,
                      address TEXT,
                      photo_path TEXT NOT NULL,
                      join_date TEXT NOT NULL,
                      expiry_date TEXT NOT NULL)''')
        conn.commit()
        conn.close()

    def add_student(self, student_data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        try:
            c.execute('''INSERT INTO students 
                         (registration_no, first_name, last_name, father_name, 
                          department, room_no, phone, email, address, photo_path, join_date, expiry_date)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (student_data['registration_no'],
                       student_data['first_name'],
                       student_data['last_name'],
                       student_data['father_name'],
                       student_data['department'],
                       student_data['room_no'],
                       student_data['phone'],
                       student_data['email'],
                       student_data['address'],
                       student_data['photo_path'],
                       student_data['join_date'],
                       student_data['expiry_date']))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print("Database Error:", e)  # Debugging
            return False
        except Exception as e:
            print("General Error:", e)  # Debugging
            return False
        finally:
            conn.close()

    def get_student(self, reg_no):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''SELECT registration_no, first_name, last_name, father_name,
                     department, room_no, phone, email, address, photo_path, join_date, expiry_date
                     FROM students WHERE registration_no = ?''', (reg_no,))
        student = c.fetchone()

        conn.close()
        return student

    def get_all_students(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''SELECT registration_no, first_name, last_name, department, room_no
                     FROM students ORDER BY last_name, first_name''')
        students = c.fetchall()

        conn.close()
        return students

    def print_db_structure(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("PRAGMA table_info(students)")
        print("Database structure:")
        for column in c.fetchall():
            print(column)
        conn.close()