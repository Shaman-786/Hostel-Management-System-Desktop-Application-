import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
from datetime import datetime
import time
from database import init_db, add_student, get_all_students, get_student_by_registration
from id_card_generator import generate_id_card


class AnimatedButton(ttk.Button):
    def __init__(self, *args, **kwargs):
        ttk.Button.__init__(self, *args, **kwargs)
        self.default_bg = self.cget('style')
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.configure(style='Hover.TButton')

    def on_leave(self, e):
        self.configure(style=self.default_bg)


class HostelManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hostel Management System")
        self.root.geometry("1100x750")
        self.root.minsize(1000, 700)

        # Configure styles
        self.configure_styles()

        # Initialize database
        init_db()

        # Setup UI
        self.setup_ui()

        # Load students with animation
        self.root.after(300, self.load_students_with_animation)

    def configure_styles(self):
        style = ttk.Style()

        # Theme settings
        style.theme_use('clam')

        # Main frame style
        style.configure('TFrame', background='#f5f5f5')

        # Label styles
        style.configure('TLabel', background='#f5f5f5', font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#2c3e50')

        # Button styles
        style.configure('TButton', font=('Segoe UI', 10), padding=6)
        style.configure('Primary.TButton', foreground='white', background='#3498db')
        style.map('Primary.TButton',
                  background=[('active', '#2980b9'), ('pressed', '#2980b9')])

        style.configure('Hover.TButton', foreground='white', background='#2980b9')
        style.configure('Success.TButton', foreground='white', background='#2ecc71')
        style.map('Success.TButton',
                  background=[('active', '#27ae60'), ('pressed', '#27ae60')])

        # Entry styles
        style.configure('TEntry', fieldbackground='white', padding=5)

        # Notebook styles
        style.configure('TNotebook', background='#f5f5f5')
        style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[10, 5])
        style.map('TNotebook.Tab',
                  background=[('selected', '#ecf0f1'), ('!selected', '#bdc3c7')],
                  foreground=[('selected', '#2c3e50'), ('!selected', '#7f8c8d')])

        # Treeview styles
        style.configure('Treeview', font=('Segoe UI', 10), rowheight=25)
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#3498db')])

    def setup_ui(self):
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add header
        self.header = ttk.Frame(self.main_container, style='TFrame')
        self.header.pack(fill=tk.X, pady=(0, 10))

        self.title_label = ttk.Label(
            self.header,
            text="HOSTEL MANAGEMENT SYSTEM",
            style='Title.TLabel'
        )
        self.title_label.pack(pady=10)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Registration Tab
        self.registration_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.registration_frame, text="Student Registration")
        self.setup_registration_tab()

        # Students List Tab
        self.students_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.students_frame, text="Students List")
        self.setup_students_tab()

        # ID Card Tab
        self.id_card_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.id_card_frame, text="ID Card Generator")
        self.setup_id_card_tab()

    def setup_registration_tab(self):
        # Main container
        reg_container = ttk.Frame(self.registration_frame)
        reg_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Form container
        form_frame = ttk.Frame(reg_container)
        form_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)

        # Form fields
        fields = [
            ("Registration No:", "registration_no"),
            ("First Name:", "first_name"),
            ("Last Name:", "last_name"),
            ("Father's Name:", "father_name"),
            ("Department:", "department"),
            ("Room No:", "room_no"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Address:", "address")
        ]

        self.entries = {}
        for i, (text, name) in enumerate(fields):
            label = ttk.Label(form_frame, text=text, style='TLabel')
            label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)

            entry = ttk.Entry(form_frame, style='TEntry')
            entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.EW)
            self.entries[name] = entry

        # Photo upload section
        photo_frame = ttk.Frame(reg_container)
        photo_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=10, pady=10)

        self.photo_label = ttk.Label(photo_frame, text="Student Photo:", style='TLabel')
        self.photo_label.pack(pady=5)

        self.photo_path = ""
        self.photo_preview = ttk.Label(photo_frame, background='white', relief=tk.SUNKEN)
        self.photo_preview.pack(pady=5, ipady=20, ipadx=20)

        upload_btn = AnimatedButton(
            photo_frame,
            text="Upload Photo",
            command=self.upload_photo,
            style='Primary.TButton'
        )
        upload_btn.pack(pady=10, ipadx=20)

        # Submit button
        submit_btn = AnimatedButton(
            reg_container,
            text="Register Student",
            command=self.register_student,
            style='Success.TButton'
        )
        submit_btn.grid(row=1, column=0, columnspan=2, pady=20)

        # Configure grid
        reg_container.grid_columnconfigure(0, weight=3)
        reg_container.grid_columnconfigure(1, weight=1)
        reg_container.grid_rowconfigure(0, weight=1)

        form_frame.grid_columnconfigure(1, weight=1)

    def setup_students_tab(self):
        # Main container
        students_container = ttk.Frame(self.students_frame)
        students_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Treeview frame with scrollbars
        tree_frame = ttk.Frame(students_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview for student list
        self.students_tree = ttk.Treeview(tree_frame, columns=(
            "reg_no", "name", "department", "room", "phone"), show="headings")

        # Configure columns
        self.students_tree.heading("reg_no", text="Registration No", anchor=tk.W)
        self.students_tree.heading("name", text="Name", anchor=tk.W)
        self.students_tree.heading("department", text="Department", anchor=tk.W)
        self.students_tree.heading("room", text="Room No", anchor=tk.W)
        self.students_tree.heading("phone", text="Phone", anchor=tk.W)

        self.students_tree.column("reg_no", width=150, anchor=tk.W)
        self.students_tree.column("name", width=250, anchor=tk.W)
        self.students_tree.column("department", width=200, anchor=tk.W)
        self.students_tree.column("room", width=100, anchor=tk.W)
        self.students_tree.column("phone", width=150, anchor=tk.W)

        # Add scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.students_tree.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.students_tree.xview)
        self.students_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # Grid layout
        self.students_tree.grid(row=0, column=0, sticky=tk.NSEW)
        y_scroll.grid(row=0, column=1, sticky=tk.NS)
        x_scroll.grid(row=1, column=0, sticky=tk.EW)

        # Configure grid weights
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Refresh button
        refresh_btn = AnimatedButton(
            students_container,
            text="Refresh List",
            command=self.load_students_with_animation,
            style='Primary.TButton'
        )
        refresh_btn.pack(pady=10, ipadx=20)

    def setup_id_card_tab(self):
        # Main container
        id_card_container = ttk.Frame(self.id_card_frame)
        id_card_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Controls frame
        controls_frame = ttk.Frame(id_card_container)
        controls_frame.pack(fill=tk.X, pady=10)

        # Registration number selection
        ttk.Label(controls_frame, text="Registration Number:", style='TLabel').pack(side=tk.LEFT, padx=5)

        self.id_card_reg_no = ttk.Combobox(controls_frame, style='TEntry')
        self.id_card_reg_no.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Buttons frame
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(side=tk.RIGHT, padx=5)

        # Preview button
        preview_btn = AnimatedButton(
            buttons_frame,
            text="Preview ID Card",
            command=self.preview_id_card,
            style='Primary.TButton'
        )
        preview_btn.pack(side=tk.LEFT, padx=5, ipadx=10)

        # Generate button
        generate_btn = AnimatedButton(
            buttons_frame,
            text="Generate PDF",
            command=self.generate_id_card_pdf,
            style='Success.TButton'
        )
        generate_btn.pack(side=tk.LEFT, padx=5, ipadx=10)

        # ID card preview frame
        preview_container = ttk.Frame(id_card_container)
        preview_container.pack(fill=tk.BOTH, expand=True)

        self.id_card_preview = ttk.Label(
            preview_container,
            background='white',
            relief=tk.SUNKEN,
            anchor=tk.CENTER
        )
        self.id_card_preview.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)

    def upload_photo(self):
        file_path = filedialog.askopenfilename(
            title="Select Student Photo",
            filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")))

        if file_path:
            try:
                # Save the photo to student_images folder
                filename = f"student_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                save_path = os.path.join('data', 'student_images', filename)

                # Open and resize the image
                img = Image.open(file_path)
                img.thumbnail((200, 200))
                img.save(save_path, "JPEG")

                # Update preview with animation
                self.animate_photo_change(img)
                self.photo_path = save_path

            except Exception as e:
                messagebox.showerror("Error", f"Failed to process image: {str(e)}")

    def animate_photo_change(self, new_img):
        # Create temporary image for animation
        temp_img = Image.new('RGB', (150, 150), (255, 255, 255))
        temp_photo = ImageTk.PhotoImage(temp_img)
        self.photo_preview.config(image=temp_photo)
        self.photo_preview.image = temp_photo

        # Resize and fade in new image
        new_img.thumbnail((150, 150))
        final_photo = ImageTk.PhotoImage(new_img)

        def fade_in(alpha):
            if alpha < 1.0:
                blended = Image.blend(temp_img, new_img, alpha)
                blended_photo = ImageTk.PhotoImage(blended)
                self.photo_preview.config(image=blended_photo)
                self.photo_preview.image = blended_photo
                self.root.after(20, fade_in, alpha + 0.05)
            else:
                self.photo_preview.config(image=final_photo)
                self.photo_preview.image = final_photo

        fade_in(0.0)

    def register_student(self):
        # Validate required fields
        if not self.entries['registration_no'].get():
            messagebox.showerror("Error", "Registration number is required")
            return

        if not self.photo_path:
            messagebox.showerror("Error", "Student photo is required")
            return

        # Collect data
        student_data = {
            'registration_no': self.entries['registration_no'].get(),
            'first_name': self.entries['first_name'].get(),
            'last_name': self.entries['last_name'].get(),
            'father_name': self.entries['father_name'].get(),
            'department': self.entries['department'].get(),
            'room_no': self.entries['room_no'].get(),
            'phone': self.entries['phone'].get(),
            'email': self.entries['email'].get(),
            'address': self.entries['address'].get()
        }

        try:
            # Add to database
            add_student(student_data, self.photo_path)

            # Generate ID card
            output_path = os.path.join('data', 'id_cards', f"{student_data['registration_no']}_id_card.pdf")
            generate_id_card(student_data, self.photo_path, output_path)

            # Clear form with animation
            self.animate_form_clear()

            # Show success message
            self.show_success_message("Student registered successfully and ID card generated!")

            # Refresh students list
            self.load_students_with_animation()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to register student: {str(e)}")

    def animate_form_clear(self):
        # Animate clearing each field
        for i, entry in enumerate(self.entries.values()):
            current_text = entry.get()
            if current_text:
                def delete_char(j, e):
                    if j >= 0:
                        e.delete(j)
                        self.root.after(20, delete_char, j - 1, e)

                self.root.after(i * 100, delete_char, len(current_text) - 1, entry)

        # Clear photo with fade out
        if hasattr(self.photo_preview, 'image') and self.photo_preview.image:
            current_img = self.photo_preview.image

            def fade_out(alpha):
                if alpha > 0:
                    blank_img = Image.new('RGB', (150, 150), (255, 255, 255))
                    blended = Image.blend(blank_img, current_img._PhotoImage__photo, alpha)
                    blended_photo = ImageTk.PhotoImage(blended)
                    self.photo_preview.config(image=blended_photo)
                    self.photo_preview.image = blended_photo
                    self.root.after(20, fade_out, alpha - 0.05)
                else:
                    self.photo_preview.config(image='')
                    self.photo_path = ""

            fade_out(1.0)

    def show_success_message(self, message):
        success_label = ttk.Label(
            self.registration_frame,
            text=message,
            foreground='green',
            font=('Segoe UI', 10, 'bold')
        )
        success_label.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        def fade_out():
            current_color = success_label.cget('foreground')
            if current_color != '#f5f5f5':
                r, g, b = success_label.winfo_rgb(current_color)
                r = max(0, r - 2000)
                g = max(0, g - 2000)
                new_color = f'#{r:04x}{g:04x}{b:04x}'[:7]
                success_label.config(foreground=new_color)
                self.root.after(50, fade_out)
            else:
                success_label.destroy()

        self.root.after(2000, fade_out)

    def load_students_with_animation(self):
        # Show loading animation
        loading_label = ttk.Label(
            self.students_frame,
            text="Loading students...",
            font=('Segoe UI', 10, 'italic')
        )
        loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        def load_data():
            # Clear existing data
            for item in self.students_tree.get_children():
                self.students_tree.delete(item)

            # Load from database
            students = get_all_students()

            # Populate treeview with animation
            def add_items(index=0):
                if index < len(students):
                    student = students[index]
                    self.students_tree.insert("", tk.END, values=(
                        student[1],  # reg_no
                        f"{student[2]} {student[3]}",  # first + last name
                        student[4],  # department
                        student[5],  # room_no
                        student[6]  # phone
                    ))
                    self.root.after(50, add_items, index + 1)
                else:
                    loading_label.destroy()
                    self.update_id_card_combobox()

            add_items()

        self.root.after(500, load_data)

    def update_id_card_combobox(self):
        students = get_all_students()
        reg_nos = [student[1] for student in students]
        self.id_card_reg_no['values'] = reg_nos

    def preview_id_card(self):
        reg_no = self.id_card_reg_no.get()
        if not reg_no:
            messagebox.showwarning("Warning", "Please select a registration number")
            return

        student = get_student_by_registration(reg_no)
        if not student:
            messagebox.showerror("Error", "Student not found")
            return

        student_data = {
            'registration_no': student[1],
            'first_name': student[2],
            'last_name': student[3],
            'father_name': student[4],
            'department': student[5],
            'room_no': student[6]
        }

        # Generate temporary PDF
        temp_path = os.path.join('data', 'temp_id_card.pdf')
        generate_id_card(student_data, student[10], temp_path)

        # Convert first page of PDF to image for preview
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(temp_path)
            if images:
                img = images[0]

                # Animate the preview appearance
                blank_img = Image.new('RGB', img.size, (255, 255, 255))

                def animate_preview(alpha):
                    if alpha <= 1.0:
                        blended = Image.blend(blank_img, img, alpha)
                        photo = ImageTk.PhotoImage(blended)
                        self.id_card_preview.config(image=photo)
                        self.id_card_preview.image = photo
                        self.root.after(20, animate_preview, alpha + 0.05)

                animate_preview(0.0)
        except ImportError:
            messagebox.showinfo("Info", "PDF preview requires pdf2image library. Install with: pip install pdf2image")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate preview: {str(e)}")

        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def generate_id_card_pdf(self):
        reg_no = self.id_card_reg_no.get()
        if not reg_no:
            messagebox.showwarning("Warning", "Please select a registration number")
            return

        student = get_student_by_registration(reg_no)
        if not student:
            messagebox.showerror("Error", "Student not found")
            return

        student_data = {
            'registration_no': student[1],
            'first_name': student[2],
            'last_name': student[3],
            'father_name': student[4],
            'department': student[5],
            'room_no': student[6]
        }

        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{reg_no}_id_card.pdf")

        if file_path:
            try:
                generate_id_card(student_data, student[10], file_path)

                # Show success animation
                success_label = ttk.Label(
                    self.id_card_frame,
                    text=f"ID card saved to:\n{file_path}",
                    foreground='green',
                    font=('Segoe UI', 10, 'bold')
                )
                success_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

                def fade_out():
                    current_color = success_label.cget('foreground')
                    if current_color != '#f5f5f5':
                        r, g, b = success_label.winfo_rgb(current_color)
                        r = max(0, r - 2000)
                        g = max(0, g - 2000)
                        new_color = f'#{r:04x}{g:04x}{b:04x}'[:7]
                        success_label.config(foreground=new_color)
                        self.root.after(50, fade_out)
                    else:
                        success_label.destroy()

                self.root.after(3000, fade_out)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate ID card: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()

    # Set window icon
    try:
        root.iconbitmap('icon.ico')  # Provide your own icon file
    except:
        pass

    # Center the window
    window_width = 1100
    window_height = 750
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    app = HostelManagementApp(root)
    root.mainloop()