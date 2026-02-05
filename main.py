import customtkinter as ctk
from tkinter import filedialog
import os
import threading
import yt_dlp
from PIL import Image
import urllib.request
import io
import json

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        self.geometry("800x600")
        self.config_file = "config.json"

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.last_url = ""

        # Title
        self.label_title = ctk.CTkLabel(self, text="YouTube Downloader", font=("Roboto", 24))
        self.label_title.grid(row=0, column=0, padx=20, pady=20)

        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.tabview.add("Download")
        self.tabview.add("Configurações")
        self.tabview.tab("Download").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Download").grid_columnconfigure(1, weight=1)
        self.tabview.tab("Configurações").grid_columnconfigure(0, weight=1)

        # URL Input
        self.frame_url = ctk.CTkFrame(self.tabview.tab("Download"), fg_color="transparent")
        self.frame_url.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.frame_url.grid_columnconfigure(0, weight=1)

        self.entry_url = ctk.CTkEntry(self.frame_url, placeholder_text="Cole o link do YouTube aqui")
        self.entry_url.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="ew")
        self.entry_url.bind("<KeyRelease>", self.on_url_change)

        # Left Side: Controls
        self.frame_controls = ctk.CTkFrame(self.tabview.tab("Download"), fg_color="transparent")
        self.frame_controls.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Type Selection (Video vs Audio)
        self.type_var = ctk.StringVar(value="video")
        self.frame_type = ctk.CTkFrame(self.frame_controls)
        self.frame_type.pack(pady=10, fill="x")
        
        self.radio_video = ctk.CTkRadioButton(self.frame_type, text="Vídeo", variable=self.type_var, value="video", command=self.update_options)
        self.radio_video.pack(side="left", padx=20, pady=10)
        self.radio_audio = ctk.CTkRadioButton(self.frame_type, text="Áudio", variable=self.type_var, value="audio", command=self.update_options)
        self.radio_audio.pack(side="left", padx=20, pady=10)
        self.radio_thumb = ctk.CTkRadioButton(self.frame_type, text="Miniatura", variable=self.type_var, value="thumbnail", command=self.update_options)
        self.radio_thumb.pack(side="left", padx=20, pady=10)

        # Options Frame (Resolution/Format)
        self.frame_options = ctk.CTkFrame(self.frame_controls)
        self.frame_options.pack(pady=10, fill="x")

        self.label_res = ctk.CTkLabel(self.frame_options, text="Resolução:")
        self.label_res.grid(row=0, column=0, padx=10, pady=10)
        self.option_res = ctk.CTkOptionMenu(self.frame_options, values=["1080p", "720p", "480p", "360p"])
        self.option_res.grid(row=0, column=1, padx=10, pady=10)

        self.label_fmt = ctk.CTkLabel(self.frame_options, text="Formato:")
        self.label_fmt.grid(row=1, column=0, padx=10, pady=10)
        self.option_fmt = ctk.CTkOptionMenu(self.frame_options, values=["mp4", "mkv"])
        self.option_fmt.grid(row=1, column=1, padx=10, pady=10)

        # Download Button
        self.btn_download = ctk.CTkButton(self.frame_controls, text="Baixar", command=self.start_download_thread, height=40, font=("Roboto", 16))
        self.btn_download.pack(pady=20, fill="x")

        # Right Side: Thumbnail Preview
        self.frame_preview = ctk.CTkFrame(self.tabview.tab("Download"), fg_color="transparent")
        self.frame_preview.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        
        self.label_thumbnail = ctk.CTkLabel(self.frame_preview, text="Pré-visualização", width=320, height=180, fg_color="gray20", corner_radius=10)
        self.label_thumbnail.pack(expand=True)

        # Status
        self.label_status = ctk.CTkLabel(self.tabview.tab("Download"), text="")
        self.label_status.grid(row=2, column=0, columnspan=2, padx=20, pady=10)

        # Paths
        self.config = self.load_config()
        self.path_video = ctk.StringVar(value=self.config.get("video", os.path.join(os.getcwd(), "downloads", "video")))
        self.path_audio = ctk.StringVar(value=self.config.get("audio", os.path.join(os.getcwd(), "downloads", "audio")))
        self.path_thumb = ctk.StringVar(value=self.config.get("thumbnail", os.path.join(os.getcwd(), "downloads", "thumbnail")))

        self.frame_paths = ctk.CTkFrame(self.tabview.tab("Configurações"))
        self.frame_paths.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.frame_paths.grid_columnconfigure(1, weight=1)

        self.btn_path_video = ctk.CTkButton(self.frame_paths, text="Pasta Vídeo", command=self.select_video_path)
        self.btn_path_video.grid(row=0, column=0, padx=10, pady=5)
        self.label_path_video = ctk.CTkLabel(self.frame_paths, textvariable=self.path_video, anchor="w")
        self.label_path_video.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.btn_path_audio = ctk.CTkButton(self.frame_paths, text="Pasta Áudio", command=self.select_audio_path)
        self.btn_path_audio.grid(row=1, column=0, padx=10, pady=5)
        self.label_path_audio = ctk.CTkLabel(self.frame_paths, textvariable=self.path_audio, anchor="w")
        self.label_path_audio.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.btn_path_thumb = ctk.CTkButton(self.frame_paths, text="Pasta Miniatura", command=self.select_thumb_path)
        self.btn_path_thumb.grid(row=2, column=0, padx=10, pady=5)
        self.label_path_thumb = ctk.CTkLabel(self.frame_paths, textvariable=self.path_thumb, anchor="w")
        self.label_path_thumb.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_config(self):
        config = {
            "video": self.path_video.get(),
            "audio": self.path_audio.get(),
            "thumbnail": self.path_thumb.get()
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f)

    def update_options(self):
        mode = self.type_var.get()
        if mode == "video":
            self.label_res.grid()
            self.option_res.grid()
            self.label_fmt.grid()
            self.option_fmt.grid()
            self.option_fmt.configure(values=["mp4", "mkv"])
            self.option_fmt.set("mp4")
        elif mode == "audio":
            self.label_res.grid_remove()
            self.option_res.grid_remove()
            self.label_fmt.grid()
            self.option_fmt.grid()
            self.option_fmt.configure(values=["mp3", "wav"])
            self.option_fmt.set("mp3")
        else: # thumbnail
            self.label_res.grid_remove()
            self.option_res.grid_remove()
            self.label_fmt.grid()
            self.option_fmt.grid()
            self.option_fmt.configure(values=["jpg", "png", "webp"])
            self.option_fmt.set("jpg")

    def select_video_path(self):
        path = filedialog.askdirectory()
        if path: 
            self.path_video.set(path)
            self.save_config()

    def select_audio_path(self):
        path = filedialog.askdirectory()
        if path: 
            self.path_audio.set(path)
            self.save_config()

    def select_thumb_path(self):
        path = filedialog.askdirectory()
        if path: 
            self.path_thumb.set(path)
            self.save_config()

    def on_url_change(self, event):
        url = self.entry_url.get()
        if url != self.last_url and ("youtube.com" in url or "youtu.be" in url):
            self.last_url = url
            self.start_check_thread()

    def start_check_thread(self):
        threading.Thread(target=self.check_task).start()

    def check_task(self):
        url = self.entry_url.get()
        if not url: return
        
        self.label_status.configure(text="Buscando informações...", text_color="white")
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                thumbnail_url = info.get('thumbnail')
                title = info.get('title')
                
                with urllib.request.urlopen(thumbnail_url) as u:
                    raw_data = u.read()
                
                image = Image.open(io.BytesIO(raw_data))
                image.thumbnail((320, 180))
                ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
                
                self.label_thumbnail.configure(image=ctk_image, text="")
                self.label_status.configure(text=f"Vídeo: {title}", text_color="green")
        except Exception as e:
            self.label_status.configure(text=f"Erro ao buscar info: {str(e)}", text_color="red")

    def start_download_thread(self):
        threading.Thread(target=self.download_task).start()

    def download_task(self):
        url = self.entry_url.get()
        if not url:
            self.label_status.configure(text="Erro: Insira uma URL.", text_color="red")
            return

        self.label_status.configure(text="Iniciando download...", text_color="white")
        self.btn_download.configure(state="disabled")
        
        try:
            download_type = self.type_var.get()
            if download_type == "video":
                output_path = self.path_video.get()
            elif download_type == "audio":
                output_path = self.path_audio.get()
            else:
                output_path = self.path_thumb.get()
            
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }

            if download_type == "audio":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.option_fmt.get(),
                        'preferredquality': '192',
                    }],
                })
            elif download_type == "video":
                res = self.option_res.get().replace("p", "")
                fmt = self.option_fmt.get()
                
                if fmt == "mp4":
                    # Prioriza áudio m4a para MP4 para garantir compatibilidade de som
                    format_str = f'bestvideo[height<={res}]+bestaudio[ext=m4a]/bestvideo[height<={res}]+bestaudio/best[height<={res}]'
                else:
                    format_str = f'bestvideo[height<={res}]+bestaudio/best[height<={res}]'

                ydl_opts.update({
                    'format': format_str,
                    'merge_output_format': fmt,
                })
            elif download_type == "thumbnail":
                ydl_opts.update({
                    'skip_download': True,
                    'writethumbnail': True,
                    'postprocessors': [{
                        'key': 'FFmpegThumbnailsConvertor',
                        'format': self.option_fmt.get(),
                    }],
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.label_status.configure(text="Download concluído!", text_color="green")
        except Exception as e:
            self.label_status.configure(text=f"Erro: {str(e)}", text_color="red")
        finally:
            self.btn_download.configure(state="normal")

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
