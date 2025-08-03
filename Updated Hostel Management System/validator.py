import re
from datetime import datetime

class Validator:
    @staticmethod
    def validate_registration_no(reg_no):
        reg_no = reg_no.strip().upper()
        return bool(re.match(r'^[A-Z]{2,3}-?\d{4,8}$', reg_no))

    @staticmethod
    def validate_name(name):
        name = name.strip()
        return bool(re.match(r'^[A-Za-z\s.\-]{2,50}$', name)) and len(name) >= 2

    @staticmethod
    def validate_phone(phone):
        phone = phone.strip()
        return bool(re.match(r'^[\+]?[0-9\s\-]{10,15}$', phone))

    @staticmethod
    def validate_email(email):
        email = email.strip()
        if not email:  # Email is optional
            return True
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

    @staticmethod
    def validate_date(date_str):
        date_str = date_str.strip()
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_room(room_no):
        room_no = room_no.strip().upper()
        return bool(re.match(r'^[A-Z0-9\-]{1,10}$', room_no)) and len(room_no) >= 1