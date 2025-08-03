import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import os
from database import Database
from id_card import IDCardGenerator
from validator import Validator


class StylishHostelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Hostel Management System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f2f5")

        # Initialize components
        self.setup_styles()
        self.db = Database()
        self.id_gen = IDCardGenerator()

        # Setup UI
        self.setup_ui()

        # Load initial data
        self.load_students()

    def setup_styles(self):
        """Configure custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')

        # Frame styles
        style.configure('TFrame', background='#f0f2f5')

        # Label styles
        style.configure('TLabel', background='#f0f2f5', font=('Helvetica', 10))
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'), foreground='#2c3e50')

        # Button styles
        style.configure('TButton', font=('Helvetica', 10), padding=6)
        style.configure('Primary.TButton', foreground='white', background='#4CAF50')
        style.map('Primary.TButton', background=[('active', '#45a049')])
        style.configure('Secondary.TButton', foreground='white', background='#2196F3')
        style.map('Secondary.TButton', background=[('active', '#1976D2')])

        # Entry styles
        style.configure('TEntry', fieldbackground='white', padding=5)

        # Notebook styles
        style.configure('TNotebook', background='#f0f2f5')
        style.configure('TNotebook.Tab', font=('Helvetica', 10, 'bold'), padding=[10, 5])
        style.map('TNotebook.Tab',
                  background=[('selected', '#ffffff'), ('!selected', '#dfe3e6')],
                  foreground=[('selected', '#2c3e50'), ('!selected', '#7f8c8d')])

    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text="🏠 HOSTEL MANAGEMENT SYSTEM",
                  style='Title.TLabel').pack(pady=5)

        # Student counter
        self.student_counter = ttk.Label(header_frame,
                                         text="Total Students: 0",
                                         font=('Helvetica', 12),
                                         background='#f0f2f5')
        self.student_counter.pack()

        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Setup tabs
        self.setup_registration_tab()
        self.setup_students_tab()
        self.setup_id_card_tab()

    def setup_registration_tab(self):
        """Setup the student registration tab"""
        reg_frame = ttk.Frame(self.notebook)
        self.notebook.add(reg_frame, text="➕ Student Registration")

        # Form fields
        fields = [
            ("Registration No*:", "registration_no"),
            ("First Name*:", "first_name"),
            ("Last Name*:", "last_name"),
            ("Father's Name*:", "father_name"),
            ("Department*:", "department"),
            ("Room No*:", "room_no"),
            ("Phone*:", "phone"),
            ("Email:", "email"),
            ("Address:", "address"),
            ("Join Date (YYYY-MM-DD)*:", "join_date")
        ]

        self.entries = {}
        for i, (label, name) in enumerate(fields):
            ttk.Label(reg_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky=tk.E)
            entry = ttk.Entry(reg_frame)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.EW)
            self.entries[name] = entry

        # Photo upload section
        self.photo_path = ""
        self.photo_preview = ttk.Label(reg_frame, relief=tk.SUNKEN, background='white')
        self.photo_preview.grid(row=0, column=2, rowspan=5, padx=10, pady=5, sticky=tk.NS)

        ttk.Button(reg_frame, text="📷 Upload Photo",
                   command=self.upload_photo,
                   style='Secondary.TButton').grid(row=5, column=2, padx=10, pady=5)

        # Submit button
        ttk.Button(reg_frame, text="✅ Register Student",
                   command=self.register_student,
                   style='Primary.TButton').grid(row=len(fields), column=0, columnspan=3, pady=10)

        # Grid configuration
        reg_frame.grid_columnconfigure(1, weight=1)

    def setup_students_tab(self):
        """Setup the students list tab"""
        students_frame = ttk.Frame(self.notebook)
        self.notebook.add(students_frame, text="👥 View Students")

        # Treeview with scrollbars
        tree_frame = ttk.Frame(students_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create treeview
        self.students_tree = ttk.Treeview(tree_frame, columns=("reg_no", "name", "dept", "room"), show="headings")

        # Configure columns
        self.students_tree.heading("reg_no", text="Registration No")
        self.students_tree.heading("name", text="Student Name")
        self.students_tree.heading("dept", text="Department")
        self.students_tree.heading("room", text="Room No")

        self.students_tree.column("reg_no", width=120)
        self.students_tree.column("name", width=200)
        self.students_tree.column("dept", width=150)
        self.students_tree.column("room", width=80)

        # Add scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.students_tree.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.students_tree.xview)
        self.students_tree.configure(yscroll=y_scroll.set, xscroll=x_scroll.set)

        # Grid layout
        self.students_tree.grid(row=0, column=0, sticky=tk.NSEW)
        y_scroll.grid(row=0, column=1, sticky=tk.NS)
        x_scroll.grid(row=1, column=0, sticky=tk.EW)

        # Configure grid weights
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Refresh button
        ttk.Button(students_frame, text="🔄 Refresh List",
                   command=self.load_students,
                   style='Secondary.TButton').pack(pady=5)

    def setup_id_card_tab(self):
        """Setup the ID card generation tab"""
        id_frame = ttk.Frame(self.notebook)
        self.notebook.add(id_frame, text="🪪 Generate ID Card")

        # Student selection
        ttk.Label(id_frame, text="Select Student:").grid(row=0, column=0, padx=5, pady=5)

        self.student_var = tk.StringVar()
        self.student_cb = ttk.Combobox(id_frame, textvariable=self.student_var, state='readonly')
        self.student_cb.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        # Buttons
        ttk.Button(id_frame, text="👀 Preview ID Card",
                   command=self.preview_id_card,
                   style='Secondary.TButton').grid(row=1, column=0, padx=5, pady=5)

        ttk.Button(id_frame, text="🖨 Generate ID Card",
                   command=self.generate_id_card,
                   style='Primary.TButton').grid(row=1, column=1, padx=5, pady=5)

        # ID card preview
        self.id_preview = ttk.Label(id_frame, relief=tk.SUNKEN, background='white')
        self.id_preview.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)

        # Grid configuration
        id_frame.grid_columnconfigure(1, weight=1)
        id_frame.grid_rowconfigure(2, weight=1)

    def upload_photo(self):
        """Handle photo upload for student registration"""
        file_path = filedialog.askopenfilename(
            title="Select Student Photo",
            filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")))

        if file_path:
            try:
                # Save to images folder
                filename = f"student_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                save_path = os.path.join('data', 'images', filename)

                # Process image
                img = Image.open(file_path)
                img.thumbnail((300, 300))
                img.save(save_path)

                # Update preview
                self.photo_path = save_path
                self.update_photo_preview(img)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to process image: {str(e)}")

    def update_photo_preview(self, img):
        """Update the photo preview label"""
        img.thumbnail((150, 150))
        photo = ImageTk.PhotoImage(img)
        self.photo_preview.config(image=photo)
        self.photo_preview.image = photo

    def validate_form(self):
        """Validate the registration form data"""
        required = {
            'registration_no': Validator.validate_registration_no,
            'first_name': Validator.validate_name,
            'last_name': Validator.validate_name,
            'father_name': Validator.validate_name,
            'department': Validator.validate_name,
            'room_no': Validator.validate_room,
            'phone': Validator.validate_phone,
            'join_date': Validator.validate_date
        }

        errors = []
        for field, validator in required.items():
            value = self.entries[field].get().strip()
            if not value:
                errors.append(f"{field.replace('_', ' ').title()} is required")
            elif not validator(value):
                errors.append(f"Invalid {field.replace('_', ' ')} format")

        if not self.photo_path:
            errors.append("Student photo is required")

        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return False
        return True

    def register_student(self):
        """Register a new student"""
        if not self.validate_form():
            return

        try:
            # Prepare student data
            student_data = {
                'registration_no': self.entries['registration_no'].get().strip().upper(),
                'first_name': self.entries['first_name'].get().strip().title(),
                'last_name': self.entries['last_name'].get().strip().title(),
                'father_name': self.entries['father_name'].get().strip().title(),
                'department': self.entries['department'].get().strip().upper(),
                'room_no': self.entries['room_no'].get().strip().upper(),
                'phone': self.entries['phone'].get().strip(),
                'email': self.entries['email'].get().strip(),
                'address': self.entries['address'].get().strip(),
                'photo_path': self.photo_path,
                'join_date': self.entries['join_date'].get().strip(),
                'expiry_date': (datetime.strptime(self.entries['join_date'].get().strip(), '%Y-%m-%d') +
                                timedelta(days=365)).strftime('%Y-%m-%d')
            }

            # Add to database
            if self.db.add_student(student_data):
                messagebox.showinfo("Success", "Student registered successfully!")
                self.clear_form()
                self.load_students()
            else:
                messagebox.showerror("Error", "Registration failed! Possible reasons:\n"
                                              "- Registration number already exists\n"
                                              "- Database error")

        except ValueError as e:
            messagebox.showerror("Date Error", f"Invalid date format: {e}\nPlease use YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def clear_form(self):
        """Clear the registration form"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.photo_preview.config(image='')
        self.photo_preview.image = None
        self.photo_path = ""

    def load_students(self):
        """Load students from database and update UI"""
        # Clear existing data
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)

        # Get students from database
        students = self.db.get_all_students()

        # Update counter
        self.student_counter.config(text=f"Total Students: {len(students)}")

        # Populate treeview
        for student in students:
            self.students_tree.insert("", tk.END, values=(
                student[0],  # reg_no
                f"{student[1]} {student[2]}",  # name
                student[3],  # dept
                student[4]  # room
            ))

        # Update combobox
        self.student_cb['values'] = [
            f"{student[0]} - {student[1]} {student[2]}"
            for student in students
        ]

    def load_demo_data(self):
        """Load demo data for testing"""
        if messagebox.askyesno("Demo Data", "Load sample demo students?"):
            demo_students = [
                {
                    "registration_no": "CS2023001",
                    "first_name": "Ali",
                    "last_name": "Khan",
                    "father_name": "Ahmed Khan",
                    "department": "COMPUTER SCIENCE",
                    "room_no": "A101",
                    "phone": "03001234567",
                    "email": "ali.khan@example.com",
                    "address": "Gulshan-e-Iqbal, Karachi",
                    "photo_path": "data/images/demo1.jpg",
                    "join_date": "2023-01-01",
                    "expiry_date": "2024-01-01"
                },
                {
                    "registration_no": "EE2023002",
                    "first_name": "Sana",
                    "last_name": "Ahmed",
                    "father_name": "Farooq Ahmed",
                    "department": "ELECTRICAL ENGINEERING",
                    "room_no": "B205",
                    "phone": "03111234567",
                    "email": "sana.ahmed@example.com",
                    "address": "Defence, Lahore",
                    "photo_path": "data/images/demo2.jpg",
                    "join_date": "2023-02-15",
                    "expiry_date": "2024-02-15"
                }
            ]

            # Add demo students
            success_count = 0
            for student in demo_students:
                if self.db.add_student(student):
                    success_count += 1

            messagebox.showinfo("Demo Data", f"Successfully loaded {success_count} demo students")
            self.load_students()

    def generate_id_card(self):
        """Generate ID card for selected student"""
        selection = self.student_var.get()
        if not selection:
            messagebox.showwarning("Warning", "Please select a student first")
            return

        try:
            reg_no = selection.split()[0]
            student = self.db.get_student(reg_no)

            if not student:
                messagebox.showerror("Error", "Student not found in database")
                return

            # Prepare student data
            student_data = {
                'registration_no': student[0],
                'first_name': student[1],
                'last_name': student[2],
                'father_name': student[3],
                'department': student[4],
                'room_no': student[5],
                'photo_path': student[9],
                'expiry_date': student[11]
            }

            # Generate ID card
            output_dir = os.path.join('data', 'id_cards')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{reg_no}_id_card.pdf")

            self.id_gen.generate(student_data, output_path)
            self.show_id_preview(output_path)

            messagebox.showinfo("Success", f"ID card generated successfully at:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ID card: {str(e)}")

    def preview_id_card(self):
        """Preview ID card before generation"""
        selection = self.student_var.get()
        if not selection:
            messagebox.showwarning("Warning", "Please select a student first")
            return

        try:
            reg_no = selection.split()[0]
            student = self.db.get_student(reg_no)

            if not student:
                messagebox.showerror("Error", "Student not found in database")
                return

            # Prepare student data
            student_data = {
                'registration_no': student[0],
                'first_name': student[1],
                'last_name': student[2],
                'father_name': student[3],
                'department': student[4],
                'room_no': student[5],
                'photo_path': student[9],
                'expiry_date': student[11]
            }

            # Create temporary PDF
            temp_path = os.path.join('data', 'temp_id_preview.pdf')
            self.id_gen.generate(student_data, temp_path)

            # Convert to image for preview
            self.show_id_preview(temp_path)

            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview ID card: {str(e)}")

    def show_id_preview(self, pdf_path):
        """Show preview of ID card"""
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path, first_page=1, last_page=1)
            if images:
                img = images[0]
                img.thumbnail((400, 250))
                photo = ImageTk.PhotoImage(img)
                self.id_preview.config(image=photo)
                self.id_preview.image = photo
        except ImportError:
            messagebox.showinfo("Info", "For PDF preview, please install:\n"
                                        "pip install pdf2image poppler")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show preview: {str(e)}")


if __name__ == "__main__":
    # Create and run application
    root = tk.Tk()

    # Center the window
    window_width = 1000
    window_height = 700
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    # Initialize application
    app = StylishHostelApp(root)

    # Start main loop
    root.mainloop()