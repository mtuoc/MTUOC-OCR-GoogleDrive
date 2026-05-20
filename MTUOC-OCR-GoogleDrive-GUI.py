import os
import time
import mimetypes
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

OUTPUT_FORMATS = {
    "Markdown (.md)": ("text/markdown", ".md"),
    "Word Document (.docx)": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
    "OpenDocument Text (.odt)": ("application/vnd.oasis.opendocument.text", ".odt"),
    "Rich Text Format (.rtf)": ("application/rtf", ".rtf"),
    "Searchable PDF (.pdf)": ("application/pdf", ".pdf"),
    "Plain Text (.txt)": ("text/plain", ".txt"),
    "EPUB E-book (.epub)": ("application/epub+zip", ".epub"),
    "Web Page HTML (.zip)": ("application/zip", ".zip")
}

SUPPORTED_EXTENSIONS = ('.pdf', '.jpg', '.jpeg', '.png', '.webp')

def get_drive_service(log_callback):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            log_callback("[*] Refreshing Google Drive credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                log_callback("[!] CONFIGURATION ERROR: 'credentials.json' is missing.")
                log_callback("[*] Opening Google Cloud Console in your browser...\n")
                webbrowser.open("https://console.cloud.google.com/")
                raise FileNotFoundError("Missing credentials.")
                
            log_callback("[*] Opening browser for account authentication...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def run_batch_ocr(input_path, is_folder, format_key, log_callback, finish_callback):
    try:
        log_callback("[*] Initializing Google Drive connection...")
        service = get_drive_service(log_callback)
        export_mime, target_ext = OUTPUT_FORMATS[format_key]
        
        # Determinar la llista de fitxers a processar
        files_to_process = []
        if is_folder:
            log_callback(f"[*] Scanning folder: {input_path}")
            for entry in os.scandir(input_path):
                if entry.is_file() and entry.name.lower().endswith(SUPPORTED_EXTENSIONS):
                    files_to_process.append(entry.path)
            files_to_process.sort()
            log_callback(f"[+] Found {len(files_to_process)} supported file(s) in folder.")
        else:
            if input_path.lower().endswith(SUPPORTED_EXTENSIONS):
                files_to_process.append(input_path)

        if not files_to_process:
            log_callback("[!] No supported files found to process.")
            finish_callback(False, "No valid files found (PDF, JPG, PNG, WEBP).")
            return

        # Processar cada fitxer del lot
        for index, input_file in enumerate(files_to_process, start=1):
            output_file = os.path.splitext(input_file)[0] + target_ext
            log_callback(f"\n[>] Processing ({index}/{len(files_to_process)}): {os.path.basename(input_file)} -> {os.path.basename(output_file)}")
            
            mime_type, _ = mimetypes.guess_type(input_file)
            if mime_type is None:
                mime_type = 'application/octet-stream'
                
            file_metadata = {
                'name': 'Temp_OCR_Document',
                'mimeType': 'application/vnd.google-apps.document'
            }
            media = MediaFileUpload(input_file, mimetype=mime_type)
            
            log_callback(f"    [*] Uploading file to Google Drive...")
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            file_id = file.get('id')

            time.sleep(3) # Pausa d'espera per a l'OCR de Google

            log_callback(f"    [*] Converting to: {format_key}...")
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
            content = request.execute()
            
            with open(output_file, 'wb') as f:
                f.write(content)

            log_callback("    [*] Cleaning up temporary cloud data...")
            service.files().delete(fileId=file_id).execute()
            log_callback(f"    [OK] Saved: {os.path.basename(output_file)}")
            time.sleep(1) # Evitar saturació de l'API entre fitxers

        log_callback("\n[OK] Batch conversion completed completely.")
        finish_callback(True, f"Successfully processed {len(files_to_process)} file(s)!")

    except Exception as e:
        log_callback(f"\n[!] Error processing batch: {e}")
        finish_callback(False, f"An error occurred during processing:\n{e}")


class MTUOC_OCR_App:
    def __init__(self, root):
        self.root = root
        self.root.title("MTUOC-OCR-GoogleDrive")
        self.root.geometry("1800x900")
        self.root.resizable(True, True)
        self.root.columnconfigure(1, weight=1)
        
        self.is_folder_mode = False # Variable de control interna
        
        # --- Secció d'Entrada ---
        self.lbl_input = tk.Label(root, text="Input (File or Folder):")
        self.lbl_input.grid(row=0, column=0, sticky="w", padx=10, pady=(15, 2))
        
        self.ent_input = tk.Entry(root)
        self.ent_input.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Marc per als botons de cerca
        self.btn_frame = tk.Frame(root)
        self.btn_frame.grid(row=0, column=2, padx=(5, 10), pady=5)
        
        self.btn_browse_file = tk.Button(self.btn_frame, text="Browse File...", command=self.browse_file)
        self.btn_browse_file.pack(side="left", padx=2)
        
        self.btn_browse_folder = tk.Button(self.btn_frame, text="Browse Folder...", command=self.browse_folder)
        self.btn_browse_folder.pack(side="left", padx=2)
        
        # --- Selector de Format ---
        self.lbl_format = tk.Label(root, text="Output Format:")
        self.lbl_format.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.selected_format = tk.StringVar(root)
        self.selected_format.set(list(OUTPUT_FORMATS.keys())[0])
        self.opt_format = tk.OptionMenu(root, self.selected_format, *OUTPUT_FORMATS.keys())
        self.opt_format.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # --- Botó de Conversió ---
        self.btn_convert = tk.Button(root, text="Start Conversion Process", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", height=2, command=self.start_conversion)
        self.btn_convert.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=15)
        
        # --- Consola de Logs ---
        self.lbl_log = tk.Label(root, text="Process Log Console:")
        self.lbl_log.grid(row=3, column=0, sticky="w", padx=10, pady=(5, 2))
        self.txt_log = scrolledtext.ScrolledText(root, height=18, state='disabled', bg="white", fg="black")
        self.txt_log.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0, 15))
        self.root.rowconfigure(4, weight=1)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Input Document or Image",
            filetypes=[("Supported Files", "*.pdf *.jpg *.jpeg *.png *.webp"), ("All Files", "*.*")]
        )
        if filename:
            self.is_folder_mode = False
            self.ent_input.delete(0, tk.END)
            self.ent_input.insert(0, filename)
            
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder Containing Documents")
        if folder:
            self.is_folder_mode = True
            self.ent_input.delete(0, tk.END)
            self.ent_input.insert(0, folder)

    def log(self, message):
        self.txt_log.config(state='normal')
        self.txt_log.insert(tk.END, message + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state='disabled')

    def start_conversion(self):
        input_path = self.ent_input.get().strip()
        format_key = self.selected_format.get()
        
        if not input_path:
            messagebox.showerror("Error", "Please select an input file or folder first.")
            return
        if not os.path.exists(input_path):
            messagebox.showerror("Error", "The specified target path does not exist.")
            return

        self.btn_convert.config(state='disabled', text="Processing Batch...", bg="#cccccc")
        
        self.txt_log.config(state='normal')
        self.txt_log.delete('1.0', tk.END)
        self.txt_log.config(state='disabled')
        
        threading.Thread(
            target=run_batch_ocr, 
            args=(input_path, self.is_folder_mode, format_key, self.log, self.on_conversion_finished),
            daemon=True
        ).start()

    def on_conversion_finished(self, success, message):
        self.btn_convert.config(state='normal', text="Start Conversion Process", bg="#4CAF50")
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Notice", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = MTUOC_OCR_App(root)
    root.mainloop()
