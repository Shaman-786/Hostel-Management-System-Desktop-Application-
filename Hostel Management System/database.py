import sqlite3
import os
from datetime import datetime


def init_db():
    if not os.path.exists('data'):
        os.makedirs('data')
        os.makedirs('data/student_images')
        os.makedirs('data/id_cards')

    conn = sqlite3.connect('data/hostel.db')
    c = conn.cursor()

    # Create students table
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  registration_no TEXT UNIQUE,
                  first_name TEXT,
                  last_name TEXT,
                  father_name TEXT,
                  department TEXT,
                  room_no TEXT,
                  phone TEXT,
                  email TEXT,
                  address TEXT,
                  photo_path TEXT,
                  registration_date TEXT)''')

    conn.commit()
    conn.close()


def add_student(student_data, photo_path):
    conn = sqlite3.connect('data/hostel.db')
    c = conn.cursor()

    c.execute('''INSERT INTO students 
                 (registration_no, first_name, last_name, father_name, 
                  department, room_no, phone, email, address, photo_path, registration_date)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (student_data['registration_no'],
               student_data['first_name'],
               student_data['last_name'],
               student_data['father_name'],
               student_data['department'],
               student_data['room_no'],
               student_data['phone'],
               student_data['email'],
               student_data['address'],
               photo_path,
               datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


def get_all_students():
    conn = sqlite3.connect('data/hostel.db')
    c = conn.cursor()

    c.execute('SELECT * FROM students ORDER BY last_name, first_name')
    students = c.fetchall()

    conn.close()
    return students


def get_student_by_registration(reg_no):
    conn = sqlite3.connect('data/hostel.db')
    c = conn.cursor()

    c.execute('SELECT * FROM students WHERE registration_no = ?', (reg_no,))
    student = c.fetchone()

    conn.close()
    return student