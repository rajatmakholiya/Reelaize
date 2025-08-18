import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading
import math
import os
import platform
import queue

# --- Core Application Class ---
class VideoSplitterApp:
    def __init__(self, root):
        """
        Initializes the main application window and its widgets.
        """
        self.root = root
        self.root.title("Video Splitter")
        self.root.geometry("600x620")
        self.root.resizable(True, True)
        # self.root.configure(bg="#2e2e2e") # Removed dark background

        # --- Light Theme Style Configuration ---
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        # General widget styles
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", foreground="black", font=('Helvetica', 10))
        self.style.configure("Title.TLabel", font=('Helvetica', 16, 'bold'), foreground="black")
        self.style.configure("Path.TLabel", font=('Helvetica', 9), foreground="#555")
        self.style.configure("TCheckbutton", background="#f0f0f0")
        
        # Button styles
        self.style.configure("TButton", padding=6, relief="flat", font=('Helvetica', 10), background="#f0f0f0")
        self.style.map("TButton",
            background=[('active', '#e0e0e0')]
        )
        
        # Accent button for the main action
        self.style.configure("Accent.TButton", font=('Helvetica', 11, 'bold'), background="#0078d7", foreground="white")
        self.style.map("Accent.TButton",
            background=[('active', '#005a9e')]
        )

        # Input field styles
        self.style.configure("TEntry", padding=5)
        self.style.configure("TCombobox", padding=5)

        # Progress bar style
        self.style.configure("TProgressbar", thickness=15, troughcolor='#e0e0e0', background='#0078d7', bordercolor="#e0e0e0")

        # Variables
        self.input_file_path = tk.StringVar()
        self.output_dir_path = tk.StringVar()
        self.clip_duration = tk.IntVar(value=60)
        self.aspect_ratio_choice = tk.StringVar(value="Original")
        self.add_subtitle = tk.BooleanVar(value=False)
        self.log_queue = queue.Queue()

        # --- UI Layout ---
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, expand=False, pady=(0, 10))

        ttk.Label(options_frame, text="Video Splitting Tool", style="Title.TLabel").pack(pady=(0, 20), anchor='w')

        input_file_frame = ttk.Frame(options_frame)
        input_file_frame.pack(fill=tk.X, pady=5)
        ttk.Label(input_file_frame, text="Video File:", width=15).pack(side=tk.LEFT, padx=(0, 10))
        self.input_label = ttk.Label(input_file_frame, text="No file selected...", style="Path.TLabel")
        self.input_label.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(input_file_frame, text="Browse...", command=self.select_input_file).pack(side=tk.RIGHT)

        output_dir_frame = ttk.Frame(options_frame)
        output_dir_frame.pack(fill=tk.X, pady=5)
        ttk.Label(output_dir_frame, text="Output Folder:", width=15).pack(side=tk.LEFT, padx=(0, 10))
        self.output_label = ttk.Label(output_dir_frame, text="No folder selected...", style="Path.TLabel")
        self.output_label.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(output_dir_frame, text="Browse...", command=self.select_output_dir).pack(side=tk.RIGHT)
        
        settings_frame = ttk.Frame(options_frame)
        settings_frame.pack(fill=tk.X, pady=(15, 5))
        ttk.Label(settings_frame, text="Clip Duration (s):", width=15).pack(side=tk.LEFT, padx=(0, 10))
        self.duration_entry = ttk.Entry(settings_frame, textvariable=self.clip_duration, width=10)
        self.duration_entry.pack(side=tk.LEFT)

        ttk.Label(settings_frame, text="Aspect Ratio:", width=12).pack(side=tk.LEFT, padx=(20, 10))
        self.ratio_combobox = ttk.Combobox(
            settings_frame, textvariable=self.aspect_ratio_choice,
            values=["Original", "Reels (9:16)", "Square (1:1)"], state="readonly"
        )
        self.ratio_combobox.pack(side=tk.LEFT)

        subtitle_frame = ttk.Frame(options_frame)
        subtitle_frame.pack(fill=tk.X, pady=5, anchor='w')
        self.subtitle_checkbox = ttk.Checkbutton(
            subtitle_frame, text="Add Part Number Text", variable=self.add_subtitle
        )
        self.subtitle_checkbox.pack(side=tk.LEFT, pady=(5,0))

        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, expand=False, pady=10)
        self.progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, 10))
        self.start_button = ttk.Button(progress_frame, text="Start Splitting", command=self.start_splitting_thread, style="Accent.TButton")
        self.start_button.pack(side=tk.RIGHT)

        self.status_label = ttk.Label(main_frame, text="Ready", anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(0, 10))

        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(log_frame, text="FFmpeg Log:").pack(anchor='w')
        self.log_text = ScrolledText(log_frame, height=10, state='disabled', bg='#ffffff', fg='black', font=('Consolas', 9), relief='solid', borderwidth=1)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5,0))

        self.check_ffmpeg()
        self.process_log_queue()

    def check_ffmpeg(self):
        try:
            command = "where" if platform.system() == "Windows" else "which"
            subprocess.run([command, "ffmpeg"], check=True, capture_output=True, startupinfo=self.get_startup_info())
            subprocess.run([command, "ffprobe"], check=True, capture_output=True, startupinfo=self.get_startup_info())
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror("FFmpeg Not Found", "FFmpeg is not installed or not in your system's PATH. Please install FFmpeg from ffmpeg.org.")
            self.root.destroy()

    def get_startup_info(self):
        if platform.system() == 'Windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            return startupinfo
        return None

    def select_input_file(self):
        filepath = filedialog.askopenfilename(title="Select a Video File", filetypes=(("Video files", "*.mp4 *.mov *.avi *.mkv"), ("All files", "*.*")))
        if filepath:
            self.input_file_path.set(filepath)
            self.input_label.config(text=os.path.basename(filepath))

    def select_output_dir(self):
        dirpath = filedialog.askdirectory(title="Select Output Folder")
        if dirpath:
            self.output_dir_path.set(dirpath)
            self.output_label.config(text=os.path.basename(dirpath))

    def start_splitting_thread(self):
        input_file = self.input_file_path.get()
        output_dir = self.output_dir_path.get()
        aspect_ratio = self.aspect_ratio_choice.get()
        add_subtitle = self.add_subtitle.get()

        try:
            clip_duration = self.clip_duration.get()
            if clip_duration <= 0:
                messagebox.showwarning("Invalid Duration", "Clip duration must be a positive number.")
                return
        except tk.TclError:
            messagebox.showwarning("Invalid Duration", "Please enter a valid number for clip duration.")
            return

        if not input_file or not output_dir:
            messagebox.showwarning("Input Missing", "Please select both an input file and an output folder.")
            return

        self.start_button.config(state=tk.DISABLED)
        self.status_label.config(text="Starting...")
        self.progress['value'] = 0
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

        thread = threading.Thread(target=self.split_video, args=(input_file, output_dir, clip_duration, aspect_ratio, add_subtitle))
        thread.daemon = True
        thread.start()

    def split_video(self, input_file, output_dir, clip_duration, aspect_ratio, add_subtitle):
        try:
            self.log_queue.put("--- Analyzing video file ---\n")
            ffprobe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_file]
            result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True, startupinfo=self.get_startup_info())
            duration = float(result.stdout)
            self.log_queue.put(f"Video duration: {duration:.2f} seconds\n")

            num_clips = 1 if duration < clip_duration else math.ceil(duration / clip_duration)
            self.progress['maximum'] = num_clips
            self.log_queue.put(f"Calculated {num_clips} clips of {clip_duration} seconds each.\n")

            _ , file_ext = os.path.splitext(os.path.basename(input_file))

            for i in range(num_clips):
                start_time = i * clip_duration
                output_filename = f"Part {i+1}{file_ext}"
                output_path = os.path.join(output_dir, output_filename)

                self.status_label.config(text=f"Processing clip {i+1} of {num_clips}...")
                self.log_queue.put(f"\n--- Generating clip {i+1}: {output_filename} ---\n")

                is_re_encoding_needed = (aspect_ratio != "Original") or add_subtitle

                if not is_re_encoding_needed:
                    ffmpeg_cmd = ["ffmpeg", "-i", input_file, "-ss", str(start_time), "-t", str(clip_duration), "-c", "copy", "-y", output_path]
                else:
                    filter_chain = ""
                    
                    if aspect_ratio == "Reels (9:16)":
                        filter_chain += "[0:v]split[original][copy];[copy]scale=w=1080:h=1920:force_original_aspect_ratio=increase,crop=w=1080:h=1920,boxblur=10:5[background];[original]scale=w=1080:h=1920:force_original_aspect_ratio=decrease[foreground];[background][foreground]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2"
                    elif aspect_ratio == "Square (1:1)":
                        filter_chain += "[0:v]split[original][copy];[copy]scale=w=1080:h=1080:force_original_aspect_ratio=increase,crop=w=1080:h=1080,boxblur=10:5[background];[original]scale=w=1080:h=1080:force_original_aspect_ratio=decrease[foreground];[background][foreground]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2"

                    if add_subtitle:
                        subtitle_text = f"Part {i+1}"
                        drawtext_filter = f"drawtext=text='{subtitle_text}':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=60:box=1:boxcolor=black@0.5:boxborderw=5"
                        if filter_chain:
                            filter_chain += f"[vid];[vid]{drawtext_filter}"
                        else:
                            filter_chain = drawtext_filter
                    
                    filter_flag = "-filter_complex" if "split" in filter_chain else "-vf"

                    ffmpeg_cmd = [
                        "ffmpeg", "-i", input_file, "-ss", str(start_time), "-t", str(clip_duration),
                        filter_flag, filter_chain,
                        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                        "-c:a", "copy", "-y", output_path
                    ]
                
                self.log_queue.put("Executing FFmpeg command:\n" + " ".join(f'"{arg}"' if ' ' in arg else arg for arg in ffmpeg_cmd) + "\n\n")

                process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, universal_newlines=True, startupinfo=self.get_startup_info())
                
                for line in iter(process.stdout.readline, ''):
                    self.log_queue.put(line)
                
                process.stdout.close()
                return_code = process.wait()

                if return_code != 0:
                    self.log_queue.put(f"\nERROR: FFmpeg exited with code {return_code}\n")
                    messagebox.showerror("FFmpeg Error", f"Error creating clip {i+1}. Check the log for details.")
                    self.reset_ui()
                    return

                self.progress['value'] = i + 1

            self.status_label.config(text="Splitting complete!")
            self.log_queue.put("\n--- All clips processed successfully! ---\n")
            messagebox.showinfo("Success", f"Successfully split the video into {num_clips} parts.")

        except subprocess.CalledProcessError as e:
            error_message = f"An error occurred while analyzing the video:\n{e.stderr}"
            self.log_queue.put(error_message)
            messagebox.showerror("Error", error_message)
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            self.log_queue.put(error_message)
            messagebox.showerror("An Unexpected Error Occurred", error_message)
        finally:
            self.reset_ui()

    def reset_ui(self):
        self.start_button.config(state=tk.NORMAL)

    def process_log_queue(self):
        """Checks the queue for new log messages and updates the ScrolledText widget."""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.config(state='normal')
                self.log_text.insert(tk.END, msg)
                self.log_text.see(tk.END) # Auto-scroll
                self.log_text.config(state='disabled')
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoSplitterApp(root)
    root.mainloop()

