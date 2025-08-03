from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
import os
from datetime import datetime


def generate_id_card(student_data, photo_path, output_path):
    # Create PDF
    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Card dimensions
    card_width = 300
    card_height = 200
    x = (width - card_width) / 2
    y = (height - card_height) / 2

    # Draw card background
    c.setFillColor(HexColor("#f0f8ff"))  # Light blue background
    c.rect(x, y, card_width, card_height, fill=1, stroke=1)

    # Add header
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(HexColor("#000080"))  # Navy blue
    c.drawCentredString(width / 2, y + card_height - 30, "HOSTEL ID CARD")

    # Add college logo (placeholder)
    # In a real app, you would use ImageReader on an actual logo file
    c.setFont("Helvetica", 10)
    c.drawString(x + 10, y + card_height - 50, "COLLEGE LOGO")

    # Add photo
    if os.path.exists(photo_path):
        photo = ImageReader(photo_path)
        c.drawImage(photo, x + 20, y + 50, width=80, height=100, preserveAspectRatio=True)

    # Add student information
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x + 120, y + card_height - 60, "Registration No:")
    c.drawString(x + 120, y + card_height - 80, "Name:")
    c.drawString(x + 120, y + card_height - 100, "Father's Name:")
    c.drawString(x + 120, y + card_height - 120, "Department:")
    c.drawString(x + 120, y + card_height - 140, "Room No:")

    c.setFont("Helvetica", 12)
    c.drawString(x + 220, y + card_height - 60, student_data['registration_no'])
    c.drawString(x + 220, y + card_height - 80, f"{student_data['first_name']} {student_data['last_name']}")
    c.drawString(x + 220, y + card_height - 100, student_data['father_name'])
    c.drawString(x + 220, y + card_height - 120, student_data['department'])
    c.drawString(x + 220, y + card_height - 140, student_data['room_no'])

    # Generate and add QR code
    from qr_generator import generate_qr_code
    qr_data = f"Student ID: {student_data['registration_no']}\nName: {student_data['first_name']} {student_data['last_name']}\nDepartment: {student_data['department']}"
    qr_temp_path = os.path.join('data', 'temp_qr.png')
    generate_qr_code(qr_data, qr_temp_path)

    qr_img = ImageReader(qr_temp_path)
    c.drawImage(qr_img, x + card_width - 90, y + 50, width=70, height=70)

    # Add footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, y + 20, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    c.save()
    os.remove(qr_temp_path)  # Clean up temporary QR code file