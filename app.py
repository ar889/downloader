import os
import threading
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, filedialog, messagebox, ttk
import yt_dlp

class UniversalVideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Video Downloader")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        # Variables
        self.url_var = StringVar()
        self.quality_var = StringVar(value="best")
        self.format_var = StringVar(value="mp4")
        self.save_path = os.getcwd()

        # UI Elements
        Label(root, text="Video URL:", font=("Arial", 12)).pack(pady=10)
        Entry(root, textvariable=self.url_var, width=50, font=("Arial", 10)).pack(pady=5)

        Label(root, text="Select Quality:", font=("Arial", 12)).pack(pady=10)
        quality_options = ["best", "1080p", "720p", "480p", "360p", "audio"]
        OptionMenu(root, self.quality_var, *quality_options).pack()

        Label(root, text="Select Format:", font=("Arial", 12)).pack(pady=10)
        format_options = ["mp4", "mkv", "webm", "mp3"]
        OptionMenu(root, self.format_var, *format_options).pack()

        Button(root, text="Choose Save Location", command=self.choose_directory, font=("Arial", 10)).pack(pady=10)
        Button(root, text="Download", command=self.start_download, font=("Arial", 12, "bold"), bg="green", fg="white").pack(pady=15)

        self.progress_label = Label(root, text="", font=("Arial", 10), fg="blue")
        self.progress_label.pack(pady=10)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=10)

    def choose_directory(self):
        self.save_path = filedialog.askdirectory()
        if not self.save_path:
            self.save_path = os.getcwd()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                downloaded_percent = float(d['_percent_str'].strip('%'))
            except ValueError:
                downloaded_percent = 0.0  # Fallback in case of unexpected formatting
            self.progress_bar['value'] = downloaded_percent
            self.progress_label.config(text=f"Downloading: {d['_percent_str']} at {d['_speed_str']}")
        elif d['status'] == 'finished':
            self.progress_bar['value'] = 100
            self.progress_label.config(text="Download complete!")
            messagebox.showinfo("Success", f"Downloaded to: {self.save_path}")

    def download_video(self):
        url = self.url_var.get().strip()
        quality = self.quality_var.get()
        file_format = self.format_var.get()

        if not url:
            messagebox.showerror("Error", "Please enter a valid video URL.")
            return

        options = {
            'format': 'best' if quality == "best" else f'bestvideo[height<={quality[:-1]}]+bestaudio/best',
            'outtmpl': os.path.join(self.save_path, f'%(title)s.{file_format}'),
            'progress_hooks': [self.progress_hook],
            'noprogress': True,  # Disable progress bar in terminal to avoid ANSI escape codes
        }

        # Handle specific quality selection
        if quality != "best":
            if quality == "audio":
                options['format'] = 'bestaudio/best'
                options['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': file_format if file_format in ["mp3", "aac", "wav"] else "mp3",
                    'preferredquality': '192',
                }]
            else:
                options['format'] = f'bestvideo[height<={quality[:-1]}]+bestaudio/best'

        self.progress_label.config(text="Starting download...")
        self.progress_bar['value'] = 0

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download video: {e}")

    def start_download(self):
        threading.Thread(target=self.download_video).start()

# Main application execution
if __name__ == "__main__":
    root = Tk()
    app = UniversalVideoDownloader(root)
    root.mainloop()
