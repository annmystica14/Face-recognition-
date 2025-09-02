import sqlite3
from datetime import datetime

# Define the subject timetable for Section A2
subject_schedule = {
    'Monday': {
        '9.00-10.00': 'SCSA2601',
        '10.00-11.00': 'SCSA1601',
        '12.15-1.15': 'SCSA1602',
        '1.15-2.15': 'SCSA1604',
        '2.15-3.15': 'ELECTIVE'
    },
    'Tuesday': {
        '9.00-10.00': 'CBCS',
        '10.00-11.00': 'SCSA1603',
        '12.15-1.15': 'ELECTIVE',
        '1.15-2.15': 'SCSA1601',
        '2.15-3.15': 'SCSA1602'
    },
    'Wednesday': {
        '9.00-10.00': 'CBCS',
        '10.00-11.00': 'SCSA1601',
        '12.15-1.15': 'SCSA1602',
        '1.15-2.15': 'SCSA2602',
        '2.15-3.15': 'SCSA2602'
    },
    'Thursday': {
        '9.00-10.00': 'CBCS',
        '10.00-11.00': 'SCSA1602',
        '12.15-1.15': 'ELECTIVE',
        '1.15-2.15': 'SCSA1603',
        '2.15-3.15': 'SCSA1604'
    },
    'Friday': {
        '9.00-10.00': 'SCSA1604',
        '10.00-11.00': 'SCSA1603',
        '12.15-1.15': 'SCSA1601',
        '1.15-2.15': 'S11APT2',
        '2.15-3.15': 'E-III'
    }
}

def init_attendance_db():
    conn = sqlite3.connect('database/attendance.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            day TEXT,
            time TEXT,
            subject TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_current_slot():
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    current_day = now.strftime('%A')
    
    time_slots = {
        '9.00-10.00': ('09:00', '10:00'),
        '10.00-11.00': ('10:00', '11:00'),
        '11.00-11.15': ('11:00', '11:15'),
        '12.15-1.15': ('12:15', '13:15'),
        '1.15-2.15': ('13:15', '14:15'),
        '2.15-3.15': ('14:15', '15:15'),
    }

    for slot, (start, end) in time_slots.items():
        if start <= current_time <= end:
            subject = subject_schedule.get(current_day, {}).get(slot)
            if subject:
                return current_day, slot, subject
    return current_day, None, None

def mark_attendance(name, status='Present'):
    date = datetime.now().strftime('%Y-%m-%d')
    day, time_slot, subject = get_current_slot()

    if not time_slot or not subject:
        return False  # Outside class time

    conn = sqlite3.connect('database/attendance.db')
    cursor = conn.cursor()

    # Check if already marked
    cursor.execute('''
        SELECT * FROM attendance WHERE name=? AND date=? AND time=? AND subject=?
    ''', (name, date, time_slot, subject))
    if cursor.fetchone():
        conn.close()
        return False  # Already marked

    # Insert new record
    cursor.execute('''
        INSERT INTO attendance (name, date, day, time, subject, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, date, day, time_slot, subject, status))

    conn.commit()
    conn.close()
    return True

   
