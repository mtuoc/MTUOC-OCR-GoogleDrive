import os
import argparse
import time
import glob
import mimetypes
import webbrowser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Mimetypes universals lligats a la seva extensió de comanda curta
FORMAT_MIMETYPES = {
    'md': 'text/markdown',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'odt': 'application/vnd.oasis.opendocument.text',
    'rtf': 'application/rtf',
    'pdf': 'application/pdf',
    'txt': 'text/plain',
    'epub': 'application/epub+zip',
    'zip': 'application/zip'
}

def get_drive_service():
    """Authenticates the user and returns the Drive service object."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[*] Refreshing Google Drive credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("[!] CONFIGURATION ERROR: 'credentials.json' is missing.")
                print("[*] Opening Google Cloud Console in your browser...\n")
                
                webbrowser.open("https://console.cloud.google.com/")
                
                # S'imprimeix la guia de configuració ben enquadrada a la terminal
                error_guide = (
                    "==========================================================\n"
                    " HOW TO GENERATE YOUR CREDENTIALS FILE:\n"
                    "==========================================================\n"
                    "1. A web browser has been opened at the Google Cloud Console.\n"
                    "2. Create a new project (e.g., 'MTUOC-OCR').\n"
                    "3. Go to 'Enabled APIs & Services', search for 'Google Drive API'\n"
                    "   and click 'Enable'.\n"
                    "4. Go to 'OAuth consent screen', choose 'External', fill in\n"
                    "   the mandatory fields, and set the status to 'Testing'.\n"
                    "5. Under 'Test users', add your own Google email address.\n"
                    "6. Go to 'Credentials' -> '+ Create Credentials' -> 'OAuth client ID'.\n"
                    "7. Select 'Desktop app' as the Application type and click 'Create'.\n"
                    "8. Download the generated JSON file, rename it exactly to:\n"
                    "   'credentials.json'\n"
                    "9. Place it in the exact same folder where this script is located.\n"
                    "=========================================================="
                )
                print(error_guide)
                raise FileNotFoundError("Missing 'credentials.json'. Setup instructions printed above.")
                
            print("[*] Opening browser for account authentication...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def process_single_file(service, input_file, output_file, target_format):
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + f".{target_format}"
        
    print(f"\n[>] Processing: {input_file} -> {output_file}")
    
    try:
        mime_type, _ = mimetypes.guess_type(input_file)
        if mime_type is None:
            mime_type = 'application/octet-stream'
            
        file_metadata = {
            'name': 'Temp_OCR_Document',
            'mimeType': 'application/vnd.google-apps.document'
        }
        media = MediaFileUpload(input_file, mimetype=mime_type)
        
        print(f"[*] Uploading {input_file} ({mime_type}) to Google Drive...")
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')

        time.sleep(3) # Pausa breu de seguretat per a l'OCR de Google

        print(f"[*] Exporting to {target_format.upper()} format...")
        export_mime = FORMAT_MIMETYPES[target_format]
        request = service.files().export_media(fileId=file_id, mimeType=export_mime)
        content = request.execute()
        
        with open(output_file, 'wb') as f:
            f.write(content)

        print("[*] Deleting temporary file from Drive...")
        service.files().delete(fileId=file_id).execute()
        print(f"[OK] Successfully saved: {output_file}")

    except Exception as e:
        print(f"[!] Error processing {input_file}: {e}")

def main():
    parser = argparse.ArgumentParser(description="MTUOC-OCR-GoogleDrive: Universal Document/Image OCR Converter")
    parser.add_argument("pattern", help="File pattern or wildcard (e.g., 'doc.pdf', '*.png')")
    parser.add_argument("-f", "--format", choices=list(FORMAT_MIMETYPES.keys()), required=True, help="Target output format")
    parser.add_argument("-o", "--output", help="Optional explicit output file name (only valid for single file inputs)", default=None)
    args = parser.parse_args()

    # Cerca de fitxers vàlids
    files = glob.glob(args.pattern)
    supported_exts = ('.pdf', '.jpg', '.jpeg', '.png', '.webp')
    valid_files = sorted([f for f in files if f.lower().endswith(supported_exts)])
    
    if not valid_files:
        print(f"[!] No supported files found matching: {args.pattern}")
        return

    print(f"[*] Found {len(valid_files)} file(s) to process.")
    
    try:
        service = get_drive_service()
    except FileNotFoundError:
        # Sortida neta del programa per terminal si falta el JSON (l'error ja s'ha explicat a dalt)
        return

    for f in valid_files:
        # Bloqueig de seguretat: si es processen lots massius evitem sobreescriptures de fitxer únic
        current_output = args.output if len(valid_files) == 1 else None
        process_single_file(service, f, current_output, args.format)
        time.sleep(1.5)

    print("\n[FINISH] All tasks completed successfully.")

if __name__ == "__main__":
    main()
