from fpdf import FPDF
import qrcode
from PIL import Image
import os
from datetime import datetime


class IDCardGenerator:
    def __init__(self):
        self.card_width = 85.6  # Standard ID card width in mm
        self.card_height = 54  # Standard ID card height in mm
        self.margin = 5
        self.logo_path = 'assets/logo.png' if os.path.exists('assets/logo.png') else None
        self.bg_path = 'assets/bg_pattern.png' if os.path.exists('assets/bg_pattern.png') else None

    def generate(self, student_data, output_path):
        try:
            # Create PDF in landscape orientation
            pdf = FPDF('L', 'mm', (self.card_width, self.card_height))
            pdf.add_page()

            # Add background if available
            if self.bg_path:
                pdf.image(self.bg_path, 0, 0, self.card_width, self.card_height)

            # Add college logo if available
            if self.logo_path:
                pdf.image(self.logo_path, self.margin, self.margin, 15)

            # Add header
            pdf.set_font('Arial', 'B', 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 5, "UNIVERSITY HOSTEL ID CARD", 0, 1, 'C')

            # Add student photo (right side)
            if os.path.exists(student_data['photo_path']):
                pdf.image(student_data['photo_path'],
                          self.card_width - self.margin - 20,  # X position (right side)
                          self.margin + 10,  # Y position
                          20, 25)  # Width and height

            # Add student information (left side)
            pdf.set_font('Arial', '', 8)
            pdf.set_xy(self.margin, self.margin + 15)  # Starting position

            info = [
                ("Reg No:", student_data['registration_no']),
                ("Name:", f"{student_data['first_name']} {student_data['last_name']}"),
                ("Father:", student_data['father_name']),
                ("Dept:", student_data['department']),
                ("Room:", student_data['room_no']),
                ("Valid:", student_data['expiry_date'])
            ]

            # Add each field to the ID card
            for label, value in info:
                pdf.cell(15, 5, label, 0, 0)  # Label
                pdf.set_font('Arial', 'B', 8)
                pdf.cell(40, 5, value, 0, 1)  # Value
                pdf.set_font('Arial', '', 8)
                pdf.ln(1)

            # Generate and add QR code (bottom right)
            qr_data = f"""
            UNIVERSITY HOSTEL ID
            Reg No: {student_data['registration_no']}
            Name: {student_data['first_name']} {student_data['last_name']}
            Dept: {student_data['department']}
            Valid Until: {student_data['expiry_date']}
            """

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=2,
                border=1,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Save QR code temporarily
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_temp_path = 'data/temp_qr.png'
            qr_img.save(qr_temp_path)

            # Add QR code to ID card
            pdf.image(qr_temp_path,
                      self.card_width - self.margin - 15,  # X position
                      self.card_height - self.margin - 15,  # Y position
                      15, 15)  # Width and height

            # Add footer
            pdf.set_font('Arial', 'I', 6)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 3, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 0, 'C')

            # Save PDF
            pdf.output(output_path)

            # Clean up temporary files
            if os.path.exists(qr_temp_path):
                os.remove(qr_temp_path)

            return True

        except Exception as e:
            print(f"Error generating ID card: {str(e)}")
            return False