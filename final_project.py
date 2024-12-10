import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import threading
import subprocess
import random

class MedicalImageSegmentationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Image Segmentation Expert")

        # Set the window size proportionally
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.9)
        self.root.geometry(f"{window_width}x{window_height}")

        # Configure the root grid layout
        self.root.grid_rowconfigure(0, weight=0)   # Title
        self.root.grid_rowconfigure(1, weight=0)   # Control + Save Address
        self.root.grid_rowconfigure(2, weight=0)   # Model selection + dataset entries
        self.root.grid_rowconfigure(3, weight=1)   # Logs, curve & results expand
        self.root.grid_columnconfigure(0, weight=1)

        self.selected_model = None
        self.models = {
            "U-Net": "UNet.py",
            "DeepLabV3": "DeepLabV3.py",
            "FCN": "FCN.py",
            "UNet++": "UNet++.py"
        }

        self.train_progress = []
        self.epoch_numbers = []

        self.setup_layout(window_width, window_height)

    def setup_layout(self, window_width, window_height):
        # Title
        title_label = tk.Label(self.root, text="Medical Image Segmentation Expert", font=("Arial", 18, "bold"))
        # 使用columnspan让标题在整行范围内居中
        title_label.grid(row=0, column=0, pady=10, sticky="n")

        # Create a frame for controls (batch size, epochs, LR, save address)
        control_frame = tk.Frame(self.root)
        control_frame.grid(row=1, column=0, pady=10, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)  # 让内部控件可居中

        # 在control_frame内部再加一个子Frame将控件集中居中
        inner_control_frame = tk.Frame(control_frame)
        inner_control_frame.pack(anchor="center")  # 居中显示

        self.add_control_buttons(inner_control_frame)
        self.add_save_address(inner_control_frame)

        # Model selection and dataset inputs frame
        selection_frame = tk.Frame(self.root)
        selection_frame.grid(row=2, column=0, pady=10, sticky="ew")
        selection_frame.grid_columnconfigure(0, weight=1)  # 让内容居中

        # 在selection_frame内部再加一个子Frame将控件集中居中
        inner_selection_frame = tk.Frame(selection_frame)
        inner_selection_frame.pack(anchor="center")

        # Put model selection and dataset input side by side
        self.add_model_selection(inner_selection_frame)
        self.add_dataset_inputs(inner_selection_frame)

        # Main area for logs, training curve and results
        main_area_frame = tk.Frame(self.root)
        main_area_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        main_area_frame.grid_rowconfigure(0, weight=0)  # logs
        main_area_frame.grid_rowconfigure(1, weight=1)  # training curve & results
        main_area_frame.grid_columnconfigure(0, weight=1)

        self.add_log_area(main_area_frame)
        self.add_result_area(main_area_frame)

    def add_control_buttons(self, frame):
        tk.Label(frame, text="Batch Size:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="-", command=self.decrease_batch_size, font=("Arial", 12)).grid(row=0, column=1, padx=5)
        self.batch_size_label = tk.Label(frame, text="5", width=5, relief=tk.SUNKEN, font=("Arial", 12))
        self.batch_size_label.grid(row=0, column=2, padx=5)
        tk.Button(frame, text="+", command=self.increase_batch_size, font=("Arial", 12)).grid(row=0, column=3, padx=5)

        tk.Label(frame, text="Total Epochs:", font=("Arial", 12)).grid(row=0, column=4, padx=5)
        tk.Button(frame, text="-", command=self.decrease_epochs, font=("Arial", 12)).grid(row=0, column=5, padx=5)
        self.epochs_label = tk.Label(frame, text="10", width=5, relief=tk.SUNKEN, font=("Arial", 12))
        self.epochs_label.grid(row=0, column=6, padx=5)
        tk.Button(frame, text="+", command=self.increase_epochs, font=("Arial", 12)).grid(row=0, column=7, padx=5)

        tk.Label(frame, text="Learning Rate:", font=("Arial", 12)).grid(row=0, column=8, padx=5)
        tk.Button(frame, text="-", command=self.decrease_learning_rate, font=("Arial", 12)).grid(row=0, column=9, padx=5)
        self.learning_rate_label = tk.Label(frame, text="0.02", width=5, relief=tk.SUNKEN, font=("Arial", 12))
        self.learning_rate_label.grid(row=0, column=10, padx=5)
        tk.Button(frame, text="+", command=self.increase_learning_rate, font=("Arial", 12)).grid(row=0, column=11, padx=5)

    def decrease_batch_size(self):
        current_size = int(self.batch_size_label["text"])
        if current_size > 1:
            self.batch_size_label["text"] = str(current_size - 1)

    def increase_batch_size(self):
        current_size = int(self.batch_size_label["text"])
        self.batch_size_label["text"] = str(current_size + 1)

    def decrease_epochs(self):
        current_epochs = int(self.epochs_label["text"])
        if current_epochs > 1:
            self.epochs_label["text"] = str(current_epochs - 1)

    def increase_epochs(self):
        current_epochs = int(self.epochs_label["text"])
        self.epochs_label["text"] = str(current_epochs + 1)

    def decrease_learning_rate(self):
        current_rate = float(self.learning_rate_label["text"])
        if current_rate > 0.01:
            self.learning_rate_label["text"] = f"{current_rate - 0.01:.2f}"

    def increase_learning_rate(self):
        current_rate = float(self.learning_rate_label["text"])
        self.learning_rate_label["text"] = f"{current_rate + 0.01:.2f}"

    def add_save_address(self, frame):
        tk.Label(frame, text="Save Address:", font=("Arial", 12)).grid(row=1, column=0, padx=5, sticky="e")
        self.save_address_entry = tk.Entry(frame, width=50)
        self.save_address_entry.grid(row=1, column=1, columnspan=9, padx=5, pady=10, sticky="ew")

        run_button = tk.Button(frame, text="Run", font=("Arial", 14, "bold"), bg="green", fg="white",
                               command=self.start_training)
        run_button.grid(row=1, column=10, columnspan=2, padx=10, sticky="w")

    def add_model_selection(self, parent_frame):
        model_frame = tk.Frame(parent_frame)
        model_frame.pack(side="left", padx=20)

        tk.Label(model_frame, text="Select Model:", font=("Arial", 12)).grid(row=0, column=0, padx=5)

        self.model_buttons = []
        for i, model_name in enumerate(self.models.keys()):
            btn = tk.Button(
                model_frame, text=model_name, font=("Arial", 12),
                command=lambda idx=i: self.select_model(idx)
            )
            btn.grid(row=0, column=i + 1, padx=5)
            self.model_buttons.append(btn)

    def select_model(self, model_index):
        for i, btn in enumerate(self.model_buttons):
            if i == model_index:
                btn.config(bg="green", fg="white")
                self.selected_model = list(self.models.keys())[i]
            else:
                btn.config(bg="SystemButtonFace", fg="black")

    def add_dataset_inputs(self, parent_frame):
        dataset_frame = tk.Frame(parent_frame)
        dataset_frame.pack(side="left", padx=20)

        tk.Label(dataset_frame, text="Train Dataset:", font=("Arial", 12)).grid(row=0, column=0, padx=5, sticky="e")
        self.train_dataset_entry = tk.Entry(dataset_frame, width=40)
        self.train_dataset_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(dataset_frame, text="Test Dataset:", font=("Arial", 12)).grid(row=1, column=0, padx=5, sticky="e")
        self.test_dataset_entry = tk.Entry(dataset_frame, width=40)
        self.test_dataset_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(dataset_frame, text="Model File (Optional):", font=("Arial", 12)).grid(row=2, column=0, padx=5, sticky="e")
        self.model_file_entry = tk.Entry(dataset_frame, width=40)
        self.model_file_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        dataset_frame.grid_columnconfigure(1, weight=1)

    def add_log_area(self, parent_frame):
        log_frame = tk.Frame(parent_frame, relief=tk.SUNKEN, bd=2)
        log_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        log_frame.grid_columnconfigure(0, weight=1)

        tk.Label(log_frame, text="Logs", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, width=100, height=10, state="disabled")
        self.log_area.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        log_frame.grid_columnconfigure(0, weight=1)

    def log_message(self, message):
        self.log_area.configure(state="normal")
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state="disabled")

    def add_result_area(self, parent_frame):
        content_frame = tk.Frame(parent_frame)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        # Left: Training Curve
        train_curve_frame = tk.Frame(content_frame, relief=tk.SUNKEN, bd=2, bg="white")
        train_curve_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tk.Label(train_curve_frame, text="Epoch Training Curve", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        figure = plt.Figure(figsize=(6, 5), dpi=100)
        self.ax = figure.add_subplot(111)
        self.ax.grid(True)
        self.ax.set_title("Training Curve")
        self.canvas = FigureCanvasTkAgg(figure, train_curve_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Right: Sample Test Results
        results_frame = tk.Frame(content_frame, relief=tk.SUNKEN, bd=2, bg="white")
        results_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        tk.Label(results_frame, text="Sample Test Results", font=("Arial", 14, "bold"), fg="blue", bg="white").pack(pady=10)

        self.result_boxes_frame = tk.Frame(results_frame, bg="white")
        self.result_boxes_frame.pack(fill=tk.BOTH, expand=True)

        self.result_boxes = []
        for i in range(2):  # 2 rows
            for j in range(3):  # 3 columns
                result_box = tk.Frame(self.result_boxes_frame, width=320, height=220, relief=tk.SUNKEN, bd=2,
                                      bg="white")
                result_box.grid(row=i, column=j, padx=20, pady=20, sticky="nsew")
                self.result_boxes.append(result_box)

        self.result_boxes_frame.grid_rowconfigure(0, weight=1)
        self.result_boxes_frame.grid_rowconfigure(1, weight=1)
        for j in range(3):
            self.result_boxes_frame.grid_columnconfigure(j, weight=1)

    def validate_paths(self):
        paths = [
            ("Train Dataset", self.train_dataset_entry.get()),
            ("Test Dataset", self.test_dataset_entry.get()),
            ("Save Address", self.save_address_entry.get())
        ]

        for label, path in paths:
            if not os.path.isdir(path):
                messagebox.showerror("Error", f"{label} path is invalid: {path}")
                return False

        model_file_path = self.model_file_entry.get()
        if model_file_path and not os.path.isfile(model_file_path):
            messagebox.showerror("Error", f"Model file path is invalid: {model_file_path}")
            return False

        return True

    def start_training(self):
        if not self.validate_paths():
            return

        if not self.selected_model:
            messagebox.showerror("Error", "Please select a model before running.")
            return

        batch_size = int(self.batch_size_label["text"])
        epochs = int(self.epochs_label["text"])
        learning_rate = float(self.learning_rate_label["text"])
        model_file_path = self.model_file_entry.get()
        script_name = self.models[self.selected_model]

        self.log_message(f"Starting process with {self.selected_model}...")
        self.log_message(f"Batch Size: {batch_size}, Epochs: {epochs}, Learning Rate: {learning_rate}")

        threading.Thread(
            target=self.run_external_model_process,
            args=(script_name, batch_size, epochs, learning_rate, model_file_path)
        ).start()

    def run_external_model_process(self, script_name, batch_size, epochs, learning_rate, model_file_path):
        try:
            train_dataset_path = self.train_dataset_entry.get()
            test_dataset_path = self.test_dataset_entry.get()
            save_address_path = self.save_address_entry.get()

            command = [
                "python", script_name,
                "--batch-size", str(batch_size),
                "--epochs", str(epochs),
                "--learning-rate", str(learning_rate),
                "--train-dataset", train_dataset_path,
                "--test-dataset", test_dataset_path,
                "--save-address", save_address_path
            ]
            if model_file_path:
                command += ["--model-file", model_file_path]

            self.log_message(f"Running external model process: {' '.join(command)}")

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            for line in iter(process.stdout.readline, ''):
                line_stripped = line.strip()
                self.log_message(line_stripped)

                if "Loss:" in line_stripped:
                    self.update_training_curve(line_stripped)

            for error_line in iter(process.stderr.readline, ''):
                self.log_message(error_line.strip())

            process.wait()
            if process.returncode == 0:
                self.log_message("Process completed successfully.")
                self.display_test_results(save_address_path)
            else:
                self.log_message("Process encountered an error.")

        except Exception as e:
            self.log_message(f"An error occurred while running the external process: {e}")

    def update_training_curve(self, log_line):
        try:
            if "Loss:" in log_line:
                loss_str = log_line.split("Loss:")[-1].strip()
                loss_value = float(loss_str)
                self.train_progress.append(loss_value)
                self.epoch_numbers.append(len(self.train_progress))

                self.ax.clear()
                self.ax.plot(self.epoch_numbers, self.train_progress, marker='o', linestyle='-', color='b')
                self.ax.set_title("Training Curve")
                self.ax.set_xlabel("Epochs")
                self.ax.set_ylabel("Loss")
                self.ax.grid(True)
                self.canvas.draw()
        except ValueError:
            pass

    def display_test_results(self, save_address):
        results_folder = os.path.join(save_address, "result_display")
        if not os.path.isdir(results_folder):
            self.log_message(f"Results folder not found: {results_folder}")
            return

        result_images = [os.path.join(results_folder, f) for f in os.listdir(results_folder) if f.endswith(".png")]
        random.shuffle(result_images)

        # Clear old images
        for box in self.result_boxes:
            for widget in box.winfo_children():
                widget.destroy()

        for box, result_image in zip(self.result_boxes, result_images[:6]):
            img = Image.open(result_image)
            img = img.resize((320, 220))
            img_tk = ImageTk.PhotoImage(img)
            label = tk.Label(box, image=img_tk)
            label.image = img_tk
            label.pack(fill=tk.BOTH, expand=True)

        self.log_message("Test results displayed.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalImageSegmentationApp(root)
    root.mainloop()
