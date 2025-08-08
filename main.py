import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
import math
import os
from ml_module import CephalometricML

class SteinerAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steiner's Cephalometric Analysis Software")
        self.root.geometry("1200x800")
        
        # Initialize ML module
        self.ml_module = CephalometricML()
        
        # Initialize landmarks dictionary
        self.landmarks = {
            'Sella (S)': {'x': None, 'y': None},
            'Nasion (N)': {'x': None, 'y': None},
            'Orbitale (Or)': {'x': None, 'y': None},
            'Porion (Po)': {'x': None, 'y': None},
            'Subspinale (A Point)': {'x': None, 'y': None},
            'Supramentale (B Point)': {'x': None, 'y': None},
            'Pogonion (Pg)': {'x': None, 'y': None},
            'Menton (Me)': {'x': None, 'y': None},
            'Gnathion (Gn)': {'x': None, 'y': None},
            'Gonion (Go)': {'x': None, 'y': None},
            'Incision Inferius (II)': {'x': None, 'y': None},
            'Incision Superius (IS)': {'x': None, 'y': None},
            'Upper lip': {'x': None, 'y': None},
            'Lower lip': {'x': None, 'y': None},
            'Subnasale (Sn)': {'x': None, 'y': None},
            'Soft tissue Pogonion (Pog\')': {'x': None, 'y': None},
            'Posterior Nasal Spine (PNS)': {'x': None, 'y': None},
            'Anterior Nasal Spine (ANS)': {'x': None, 'y': None},
            'Articulare (Ar)': {'x': None, 'y': None}
        }
        
        # Store current measurements
        self.current_measurements = None
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create frames for each tab
        self.image_frame = ttk.Frame(self.notebook)
        self.analysis_frame = ttk.Frame(self.notebook)
        self.interpretation_frame = ttk.Frame(self.notebook)
        self.ml_frame = ttk.Frame(self.notebook)  # New ML training tab
        
        self.notebook.add(self.image_frame, text="Image & Landmarks")
        self.notebook.add(self.analysis_frame, text="Steiner's Analysis")
        self.notebook.add(self.interpretation_frame, text="Interpretation Guide")
        self.notebook.add(self.ml_frame, text="ML Training")  # Add ML tab
        
        # Build each tab
        self.create_image_tab()
        self.create_analysis_tab()
        self.create_interpretation_tab()
        self.create_ml_tab()  # Create ML tab
        
        # Load default image (optional)
        self.current_image = None
        self.photo = None
        self.landmark_buttons = []
        self.scale_x = 1.0
        self.scale_y = 1.0

    def create_image_tab(self):
        # Left panel for image display
        left_panel = ttk.Frame(self.image_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image canvas
        self.image_canvas = tk.Canvas(left_panel, bg='gray', width=600, height=700)
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right panel for controls
        right_panel = ttk.Frame(self.image_frame, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Upload button
        upload_btn = ttk.Button(right_panel, text="Upload Cephalogram", command=self.upload_image)
        upload_btn.pack(fill=tk.X, pady=5)
        
        # Auto-detect button
        detect_btn = ttk.Button(right_panel, text="Auto-Detect Landmarks", command=self.auto_detect_landmarks)
        detect_btn.pack(fill=tk.X, pady=5)
        
        # Manual landmark selection
        ttk.Label(right_panel, text="Manual Landmark Selection:").pack(pady=(10, 0))
        
        self.landmark_var = tk.StringVar()
        landmark_dropdown = ttk.Combobox(right_panel, textvariable=self.landmark_var, 
                                       values=list(self.landmarks.keys()))
        landmark_dropdown.pack(fill=tk.X, pady=5)
        
        select_btn = ttk.Button(right_panel, text="Select Landmark on Image", 
                               command=self.prepare_landmark_selection)
        select_btn.pack(fill=tk.X, pady=5)
        
        # Clear landmarks button
        clear_btn = ttk.Button(right_panel, text="Clear All Landmarks", command=self.clear_landmarks)
        clear_btn.pack(fill=tk.X, pady=5)
        
        # Landmark status display
        ttk.Label(right_panel, text="Landmark Status:").pack(pady=(10, 0))
        self.landmark_status = tk.Text(right_panel, height=10, width=30)
        self.landmark_status.pack(fill=tk.BOTH, expand=True)
        
        # Update status
        self.update_landmark_status()

    def create_analysis_tab(self):
        # Main container
        container = ttk.Frame(self.analysis_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Analysis button
        analyze_btn = ttk.Button(container, text="Perform Steiner's Analysis", command=self.perform_analysis)
        analyze_btn.pack(pady=10)
        
        # Results display
        self.results_text = tk.Text(container, height=30, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_interpretation_tab(self):
        canvas = tk.Canvas(self.interpretation_frame)
        scrollbar = ttk.Scrollbar(self.interpretation_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Interpretation content
        ttk.Label(scrollable_frame, text="Steiner's Analysis Interpretation Guide", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Skeletal Relationships
        skeletal_frame = ttk.LabelFrame(scrollable_frame, text="Skeletal Relationships")
        skeletal_frame.pack(fill=tk.X, padx=5, pady=5, ipadx=5, ipady=5)
        
        # SNA Interpretation
        ttk.Label(skeletal_frame, text="SNA (82° ± 2)", font=('Arial', 9, 'bold')).pack(anchor='w')
        ttk.Label(skeletal_frame, text="Normal (80-84°): Maxilla in normal sagittal position", foreground='green').pack(anchor='w')
        ttk.Label(skeletal_frame, text="High (>84°): Prognathic maxilla", foreground='red').pack(anchor='w')
        ttk.Label(skeletal_frame, text="Low (<80°): Retrognathic maxilla", foreground='red').pack(anchor='w')
        
        # SNB Interpretation
        ttk.Label(skeletal_frame, text="SNB (80° ± 2)", font=('Arial', 9, 'bold')).pack(anchor='w', pady=(5,0))
        ttk.Label(skeletal_frame, text="Normal (78-82°): Mandible in normal sagittal position", foreground='green').pack(anchor='w')
        ttk.Label(skeletal_frame, text="High (>82°): Prognathic mandible", foreground='red').pack(anchor='w')
        ttk.Label(skeletal_frame, text="Low (<78°): Retrognathic mandible", foreground='red').pack(anchor='w')

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            self.current_image = Image.open(file_path)
            self.display_image()
            self.clear_landmarks()

    def display_image(self):
        if self.current_image:
            # Clear previous landmarks
            for btn in self.landmark_buttons:
                self.image_canvas.delete(btn)
            self.landmark_buttons = []
            
            # Resize image to fit canvas
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            # Get image dimensions
            img_width, img_height = self.current_image.size
            
            # Calculate scaling factors
            ratio = min(canvas_width/img_width, canvas_height/img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            # Resize image
            resized_image = self.current_image.resize((new_width, new_height), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_image)
            
            # Display image
            self.image_canvas.create_image(canvas_width//2, canvas_height//2, anchor=tk.CENTER, image=self.photo)
            
            # Store scaling factors
            self.scale_x = new_width / img_width
            self.scale_y = new_height / img_height

    def auto_detect_landmarks(self):
        messagebox.showinfo("Info", "Auto-detection would be implemented with a trained model in a full implementation")

    def prepare_landmark_selection(self):
        landmark_name = self.landmark_var.get()
        if landmark_name and self.current_image:
            self.image_canvas.bind("<Button-1>", lambda event: self.set_landmark_position(event, landmark_name))
            messagebox.showinfo("Info", f"Click on the image to set {landmark_name}")

    def set_landmark_position(self, event, landmark_name):
        # Convert canvas coordinates to image coordinates
        canvas_x = event.x
        canvas_y = event.y
        
        # Calculate image coordinates
        img_x = int(canvas_x / self.scale_x)
        img_y = int(canvas_y / self.scale_y)
        
        # Update landmark position
        self.landmarks[landmark_name]['x'] = img_x
        self.landmarks[landmark_name]['y'] = img_y
        
        # Update display
        self.update_landmark_display()
        self.update_landmark_status()
        
        # Unbind the click event
        self.image_canvas.unbind("<Button-1>")

    def clear_landmarks(self):
        for name in self.landmarks:
            self.landmarks[name]['x'] = None
            self.landmarks[name]['y'] = None
        self.update_landmark_display()
        self.update_landmark_status()

    def update_landmark_display(self):
        # Clear existing landmarks
        for btn in self.landmark_buttons:
            self.image_canvas.delete(btn)
        self.landmark_buttons = []
        
        # Draw new landmarks
        for name, pos in self.landmarks.items():
            if pos['x'] is not None and pos['y'] is not None:
                # Scale coordinates to canvas size
                canvas_x = pos['x'] * self.scale_x
                canvas_y = pos['y'] * self.scale_y
                
                # Draw landmark
                dot = self.image_canvas.create_oval(
                    canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5,
                    fill='red', outline='black'
                )
                text = self.image_canvas.create_text(
                    canvas_x, canvas_y-10,
                    text=name.split(' ')[0], fill='blue', anchor=tk.S
                )
                self.landmark_buttons.extend([dot, text])

    def update_landmark_status(self):
        self.landmark_status.delete(1.0, tk.END)
        for name, pos in self.landmarks.items():
            status = "✓" if pos['x'] is not None else "✗"
            color = "green" if pos['x'] is not None else "red"
            self.landmark_status.insert(tk.END, f"{name}: {status}\n", color)
            self.landmark_status.tag_config(color, foreground=color)

    def calculate_angle_between_lines(self, v1, v2):
        """Calculate the acute angle between two lines in degrees"""
        # Calculate dot product
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        
        # Calculate magnitudes
        mag_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
        mag_v2 = math.sqrt(v2[0]**2 + v2[1]**2)
        
        # Avoid division by zero
        if mag_v1 == 0 or mag_v2 == 0:
            return 0.0
        
        # Calculate cosine of the angle
        cosine_angle = dot_product / (mag_v1 * mag_v2)
        cosine_angle = max(-1, min(1, cosine_angle))  # Clamp to avoid numerical errors
        
        # Calculate angle in degrees
        angle = math.degrees(math.acos(cosine_angle))
        
        # Return the acute angle (always between 0 and 90 degrees)
        return min(angle, 180 - angle)

    def calculate_sna(self):
        S = (self.landmarks['Sella (S)']['x'], self.landmarks['Sella (S)']['y'])
        N = (self.landmarks['Nasion (N)']['x'], self.landmarks['Nasion (N)']['y'])
        A = (self.landmarks['Subspinale (A Point)']['x'], self.landmarks['Subspinale (A Point)']['y'])
        
        # SNA is the angle between SN line and NA line
        sn_vector = (N[0] - S[0], N[1] - S[1])
        na_vector = (A[0] - N[0], A[1] - N[1])
        
        return self.calculate_angle_between_lines(sn_vector, na_vector)

    def calculate_snb(self):
        S = (self.landmarks['Sella (S)']['x'], self.landmarks['Sella (S)']['y'])
        N = (self.landmarks['Nasion (N)']['x'], self.landmarks['Nasion (N)']['y'])
        B = (self.landmarks['Supramentale (B Point)']['x'], self.landmarks['Supramentale (B Point)']['y'])
        
        # SNB is the angle between SN line and NB line
        sn_vector = (N[0] - S[0], N[1] - S[1])
        nb_vector = (B[0] - N[0], B[1] - N[1])
        
        return self.calculate_angle_between_lines(sn_vector, nb_vector)

    def calculate_ui_na_angle(self):
        N = (self.landmarks['Nasion (N)']['x'], self.landmarks['Nasion (N)']['y'])
        A = (self.landmarks['Subspinale (A Point)']['x'], self.landmarks['Subspinale (A Point)']['y'])
        IS = (self.landmarks['Incision Superius (IS)']['x'], self.landmarks['Incision Superius (IS)']['y'])
        
        # UI-NA angle is between upper incisor axis and NA line
        ui_root = (IS[0], IS[1] + 30)  # Estimated root position
        ui_vector = (IS[0] - ui_root[0], IS[1] - ui_root[1])
        na_vector = (A[0] - N[0], A[1] - N[1])
        
        return self.calculate_angle_between_lines(ui_vector, na_vector)

    def calculate_li_nb_angle(self):
        N = (self.landmarks['Nasion (N)']['x'], self.landmarks['Nasion (N)']['y'])
        B = (self.landmarks['Supramentale (B Point)']['x'], self.landmarks['Supramentale (B Point)']['y'])
        II = (self.landmarks['Incision Inferius (II)']['x'], self.landmarks['Incision Inferius (II)']['y'])
        
        # LI-NB angle is between lower incisor axis and NB line
        li_root = (II[0], II[1] - 30)  # Estimated root position
        li_vector = (II[0] - li_root[0], II[1] - li_root[1])
        nb_vector = (B[0] - N[0], B[1] - N[1])
        
        return self.calculate_angle_between_lines(li_vector, nb_vector)

    def calculate_ui_li_angle(self):
        IS = (self.landmarks['Incision Superius (IS)']['x'], self.landmarks['Incision Superius (IS)']['y'])
        II = (self.landmarks['Incision Inferius (II)']['x'], self.landmarks['Incision Inferius (II)']['y'])
        
        # UI-LI angle is between upper and lower incisor axes
        ui_root = (IS[0], IS[1] + 30)
        ui_vector = (IS[0] - ui_root[0], IS[1] - ui_root[1])
        
        li_root = (II[0], II[1] - 30)
        li_vector = (II[0] - li_root[0], II[1] - li_root[1])
        
        angle = self.calculate_angle_between_lines(ui_vector, li_vector)
        return 180 - angle  # Interincisal angle is the supplement

    def perform_analysis(self):
        # Check if required landmarks are set
        required_landmarks = ['Sella (S)', 'Nasion (N)', 'Subspinale (A Point)', 
                             'Supramentale (B Point)', 'Incision Inferius (II)', 
                             'Incision Superius (IS)']
        
        missing = [name for name in required_landmarks if self.landmarks[name]['x'] is None]
        if missing:
            messagebox.showerror("Error", f"Missing required landmarks: {', '.join(missing)}")
            return
            
        try:
            # Get ML predictions if available
            ml_predictions = self.ml_module.predict_measurements(self.landmarks)
            
            # Calculate measurements
            measurements = {
                'SNA': self.calculate_sna(),
                'SNB': self.calculate_snb(),
                'ANB': None,
                'UI_NA': self.calculate_ui_na_angle(),
                'LI_NB': self.calculate_li_nb_angle(),
                'UI_LI': self.calculate_ui_li_angle()
            }
            measurements['ANB'] = measurements['SNA'] - measurements['SNB']
            
            # Store current measurements
            self.current_measurements = measurements
            
            # Update ML tab with current values
            for measure, value in measurements.items():
                self.current_values[measure].set(f"{value:.1f}")
            
            # Generate results text
            results = "=== MEASUREMENTS ===\n\n"
            
            for measure, value in measurements.items():
                results += f"{measure}: {value:.1f}°"
                if ml_predictions and ml_predictions[measure] is not None:
                    ml_value = ml_predictions[measure]
                    results += f" (ML suggested: {ml_value:.1f}°)"
                results += "\n"
            
            # Add interpretation
            results += "\n=== INTERPRETATION ===\n\n"
            
            # Skeletal pattern
            if 0 <= measurements['ANB'] <= 4:
                results += "• Class I skeletal pattern\n"
            elif measurements['ANB'] > 4:
                results += "• Class II skeletal pattern\n"
            else:
                results += "• Class III skeletal pattern\n"
                
            # Upper incisor inclination
            if 18 <= measurements['UI_NA'] <= 26:
                results += "• Normal upper incisor inclination\n"
            elif measurements['UI_NA'] > 26:
                results += "• Proclined upper incisors\n"
            else:
                results += "• Retroclined upper incisors\n"
                
            # Lower incisor inclination
            if 21 <= measurements['LI_NB'] <= 29:
                results += "• Normal lower incisor inclination\n"
            elif measurements['LI_NB'] > 29:
                results += "• Proclined lower incisors\n"
            else:
                results += "• Retroclined lower incisors\n"
                
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, results)
            
            # Switch to analysis tab
            self.notebook.select(self.analysis_frame)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during analysis: {str(e)}")

    def create_ml_tab(self):
        """Create the ML training tab"""
        # Main container
        container = ttk.Frame(self.ml_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Current measurements frame
        current_frame = ttk.LabelFrame(container, text="Current Measurements")
        current_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.current_values = {}
        for measure in ['SNA', 'SNB', 'ANB', 'UI_NA', 'LI_NB', 'UI_LI']:
            frame = ttk.Frame(current_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(frame, text=f"{measure}:").pack(side=tk.LEFT)
            var = tk.StringVar()
            self.current_values[measure] = var
            ttk.Entry(frame, textvariable=var).pack(side=tk.RIGHT, expand=True)
        
        # Correction frame
        correction_frame = ttk.LabelFrame(container, text="Enter Correct Values")
        correction_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.corrected_values = {}
        for measure in ['SNA', 'SNB', 'ANB', 'UI_NA', 'LI_NB', 'UI_LI']:
            frame = ttk.Frame(correction_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(frame, text=f"{measure}:").pack(side=tk.LEFT)
            var = tk.StringVar()
            self.corrected_values[measure] = var
            ttk.Entry(frame, textvariable=var).pack(side=tk.RIGHT, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add to Training Data", 
                   command=self.add_training_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Retrain Model", 
                   command=self.retrain_model).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.ml_status = tk.Text(container, height=5, width=50)
        self.ml_status.pack(fill=tk.X, padx=5, pady=5)

    def add_training_data(self):
        """Add current measurements and corrections to training data"""
        try:
            correct_measurements = {}
            for measure in self.corrected_values:
                value = float(self.corrected_values[measure].get())
                correct_measurements[measure] = value
            
            self.ml_module.add_training_example(self.landmarks, correct_measurements)
            self.ml_status.insert(tk.END, "Training example added successfully\n")
            
            # Clear correction entries
            for var in self.corrected_values.values():
                var.set("")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values for all measurements")

    def retrain_model(self):
        """Retrain the ML model with accumulated data"""
        success, message = self.ml_module.retrain_model()
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showwarning("Warning", message)

def main():
    root = tk.Tk()
    app = SteinerAnalysisApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 