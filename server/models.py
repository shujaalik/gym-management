import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="db.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.execute_query("""CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            membership_type TEXT NOT NULL,
            program TEXT NOT NULL,
            fee_status TEXT DEFAULT 'Pending'
        )""")
        self.execute_query("""CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            check_in_time TEXT,
            check_out_time TEXT,
            FOREIGN KEY (member_id) REFERENCES members (id)
        )""")

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.connection.commit()

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

class Member:
    def __init__(self, name, membership_type, program, fee_status="Pending"):
        self.name = name
        self.membership_type = membership_type
        self.program = program
        self.fee_status = fee_status

    def save(self):
        db = Database()
        query = "INSERT INTO members (name, membership_type, program, fee_status) VALUES (?, ?, ?, ?)"
        db.execute_query(query, (self.name, self.membership_type, self.program, self.fee_status))

    @classmethod
    def all(cls):
        db = Database()
        query = "SELECT * FROM members"
        members = db.fetch_all(query)
        return [cls(*member[1:]) for member in members]

    def update_fee_status(self, fee_status):
        db = Database()
        query = "UPDATE members SET fee_status = ? WHERE name = ?"
        db.execute_query(query, (fee_status, self.name))

class Attendance:
    def __init__(self, member_id, check_in_time=None, check_out_time=None):
        self.member_id = member_id
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time

    def record_check_in(self):
        db = Database()
        query = "INSERT INTO attendance (member_id, check_in_time) VALUES (?, ?)"
        db.execute_query(query, (self.member_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def record_check_out(self):
        db = Database()
        query = """UPDATE attendance SET check_out_time = ? WHERE member_id = ? AND check_out_time IS NULL"""
        db.execute_query(query, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.member_id))

    @classmethod
    def all(cls):
        db = Database()
        query = """SELECT a.id, m.name, a.check_in_time, a.check_out_time
                   FROM attendance a
                   JOIN members m ON a.member_id = m.id"""
        records = db.fetch_all(query)
        return records