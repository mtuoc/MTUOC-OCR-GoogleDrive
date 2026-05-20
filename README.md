#MTUOC-OCR-GoogleDrive Suite

Welcome to the official technical manual and deployment documentation for the **MTUOC-OCR-GoogleDrive** suite. This software ecosystem harnesses the Google Drive API—utilizing the same deep-learning contextual neural network engine that powers Google Lens—to deliver high-precision, localized, and fully automated Optical Character Recognition (OCR).

The architecture is split into two specialized deployment workflows sharing a unified functional core:
1. **Graphical User Interface (GUI):** `MTUOC-OCR-GoogleDrive-GUI.py` – Engineered for interactive desktop operations with native support for both single-file and directory-wide batch processing.
2. **Command-Line Interface (CLI):** `MTUOC-OCR-GoogleDrive.py` – Optimized for high-throughput headless server execution, automation scripting, and pattern-matching batch file parsing.

---

## 1. Pre-Compiled Standalone Windows Binaries

For enterprise environments or workstations deploying this suite on Windows where Python runtimes and manual dependency trees are not desired, pre-compiled standalone executable files (`.exe`) are available.

* Navigate to the **Releases** section of this GitHub repository.
* Download the latest compressed distribution archive containing the compiled binaries for either the GUI or CLI application.
* Extract the archive to a local folder and run the executables directly without any prerequisite runtime environments.

*Note: Even when utilizing standalone binaries, you must generate and supply a valid `credentials.json` configuration asset as detailed in Section 3.*

---

## 2. Runtime Environment & Dependencies (Python Native)

To execute the core scripts natively, a Python 3.7+ installation is required. 

### Step 1: Component Declaration
Create a `requirements.txt` file within your root deployment directory and paste the following official Google client library specifications. Alternativelly you can use the requirements.txt file provided in the distribution:

```text
google-api-python-client>=2.0.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=1.0.0
```

### Step 2: Install required libraries
Open your system terminal or command prompt, change directory to the project root, and execute the installation via pip:

```bash
pip install -r requirements.txt
```

*Note: Modules such as `tkinter`, `webbrowser`, `os`, `time`, `mimetypes`, `threading`, and `glob` are integral components of the core Python standard library and do not require external installation.*

---

## 3. Setting up the Google Cloud API Authentication

To safely interface with Google's cloud-based OCR virtualization layers, you must declare an explicit API project within the Google Cloud Console. The suite incorporates an automated fallback handler that intercepts missing configurations and opens the management console to streamline onboarding.

### Complete Walkthrough to Generate `credentials.json`:
1. Execute either `MTUOC-OCR-GoogleDrive-GUI.py` or `MTUOC-OCR-GoogleDrive.py`. If the configuration file is missing from the root path, the script will automatically launch your default browser directly into the Google Cloud Console.
2. **Project Creation:** Open the project dropdown selector located in the top navigation header, select **New Project**, and allocate a unique descriptor (e.g., `MTUOC-OCR`).
3. **API Activation:** Expand the left-hand navigation drawer, choose **APIs & Services** > **Library**. Input **"Google Drive API"** into the search field, select the asset, and click **Enable**.
4. **OAuth Consent Configuration:** Navigate to the **OAuth consent screen** interface. Set the user type scope to **External**, fill out the mandatory metadata blocks (Application name, user support email, and developer contact details), and proceed to save.
5. **Publishing State & Test Access:** Leave the publishing cycle status as **Testing**. Under the **Test users** matrix, click *+ Add Users* and register the exact Google email address you intend to use with this application.
6. **Credential Provisioning:** Go to **Credentials** > **+ Create Credentials** > **OAuth client ID**.
7. **Application Profile:** Set the Application type dropdown strictly to **Desktop app** and click **Create**.
8. **Payload Extraction:** Click the download icon on the newly generated entry to pull the client secrets JSON file.
9. **Deployment:** Rename the downloaded file precisely to **`credentials.json`** and place it in the exact directory where the application scripts reside.

### Cryptographic Token Caching (`token.json`):
Upon initiating the first batch or file conversion with `credentials.json` present, the application will redirect your browser to a secure Google identity portal. Log in, bypass the unverified app warning (this reflects your project being in sandboxed testing mode), and grant the structural permissions. This workflow caches a local, persistent OAuth refresh token named `token.json`, ensuring all subsequent automated or manual tasks execute silently without requiring web browser interactions.

---

## 4. Manual: Graphical User Interface (GUI)

The GUI application provides an intuitive desktop environment optimized for multi-format conversion pipelines.

### Core Interface Layout & Engineering:
* **Polymorphic Input Vector:** Accepts individual files or entire folders. 
* **Dynamic Search Architecture:** Features distinct **"Browse File..."** and **"Browse Folder..."** hooks. When choosing a directory, the backend automatically runs an asynchronous multi-extension lookahead to parse files matching `.pdf`, `.jpg`, `.jpeg`, `.png`, and `.webp`.
* **Output Format Selector:** A standardized dropdown exposing the 8 cloud-virtualized export targets.
* **Non-Blocking Operation:** The system spins up separate worker threads (`threading.Thread`) for file mutations, preserving fluid UI responsiveness at 60 FPS while background OCR operations take place.
* **Interactive Log Console:** A real-time execution feedback monitor. Crucially, the log canvas is completely interactive, selectable, and copiable. Users can freely highlight segments or use `Ctrl+A` / `Ctrl+C` to copy error logs, setup guides, or path configurations without formatting degradation.

### Operational Workflow:
1. Initialize the script: `python3 MTUOC-OCR-GoogleDrive-GUI.py`.
2. To process an isolated asset, click **Browse File...**. To process an entire directory containing mixed assets, click **Browse Folder...**.
3. Set your target extension from the **Output Format** dropdown menu.
4. Click **Start Conversion Process**. The UI locks execution buttons to prevent race conditions, clears previous caches, and streams live upload/OCR statuses to the log console.

---

## 5. Manual: Command-Line Interface (CLI)

The CLI binary represents the high-efficiency alternative, engineered for execution inside bash scripts, cron jobs, remote SSH servers, or complex batch pipelines.

### Argument Architecture:
* `pattern`: Defines the explicit path, relative target, or file system wildcard string (Required positional argument).
* `-f`, `--format`: Specifies the targeted text or document representation (Required named argument). Valid flags: `md`, `docx`, `odt`, `rtf`, `pdf`, `txt`, `epub`, `zip`.

### Real-World Terminal Deployments:

1. **Convert a Single Flat PNG Image to Clean Markdown:**
   ```bash
   python3 MTUOC-OCR-GoogleDrive.py screenshot.png -f md
   ```

2. **Convert a Scanned Document into an Editable Microsoft Word File:**
   ```bash
   python3 MTUOC-OCR-GoogleDrive.py legal_scan.pdf -f docx
   ```

3. **Wildcard Directory Execution: Mass Convert All PNG Images Within a Target Subdirectory to Plain Text:**
   ```bash
   python3 MTUOC-OCR-GoogleDrive.py "images/*.png" -f txt
   ```

4. **Mixed Wildcard Batching: Extract Text From All Supported Assets Matching a Prefix into OpenDocument Text:**
   ```bash
   python3 MTUOC-OCR-GoogleDrive.py "archive_2026_*" -f odt
   ```

---

## 6. Matrix of Supported Cloud-Virtualized Output Formats

The suite relies on Google Drive’s underlying export structures, converting raw visual layouts directly into highly clean semantic schemas:

| CLI Extension Flag | GUI Selection Label | Target Characteristics & Canonical Use Cases |
| :---: | :--- | :--- |
| md | Markdown | Structured markdown syntax tailored for documentation, static site generators, and GitHub repositories. |
| docx | Word Document | Microsoft Word Open XML standard document format for traditional word processing workflows. |
| odt | OpenDocument Text | Standardized open-source text format natively processed by suites like LibreOffice and OpenOffice. |
| rtf | Rich Text Format | Universally accessible enriched text encoding designed for maximum legacy software cross-compatibility. |
| pdf | Searchable PDF | Highly Powerful: Transforms a visual-only scanned PDF or flat image file into an optimized PDF embedded with an interactive, searchable (Ctrl+F), and searchable OCR text overlay. |
| txt | Plain Text | Stripped raw text output completely devoid of styling, formatting, or assets. Excellent for clean copy-pasting or training MT corpora. |
| epub | EPUB E-book | Converts extracted textual assets into a responsive digital book asset suitable for e-readers and tablets. |
| zip | Web Page HTML | Exports the asset as a clean, zipped HTML webpage bundle containing formatted hypertext structure alongside any extracted graphics. |

---

## 7. Underlying OCR Architecture and Zero-Configuration Multilingual Modeling

Legacy offline Optical Character Recognition applications (such as basic deployments of *Tesseract*) rely heavily on strict linguistic dictionary initializations, forcing users to declare precise language parameters at runtime (e.g., `-l cat` to capture Catalan characters) to prevent severe encoding corruption on elements like the ce trencada (ç) or grave accents. 

The **MTUOC-OCR-GoogleDrive** ecosystem operates on an entirely distinct cloud-based computer vision architecture:

1. **Structural Layout Profiling:** Prior to text processing, deep-learning models evaluate spatial orientation and typographic script classifications (e.g., distinguishing Latin script configurations from Cyrillic or East Asian variants).
2. **Contextual Neural Analysis:** The processing framework evaluates characters holistically as part of larger semantic phrases rather than treating individual glyphs in isolation. Statistical linguistic models infer semantic intent, dynamically capturing vocabulary, grammar, and specialized accents based on sentence context.
3. **True Multilingual Concurrency:** Because the system evaluates text semantically rather than testing against a single localized dictionary, a single input file containing alternating paragraphs of disparate languages (e.g., a Catalan source text featuring embedded English and Spanish quotations) will process concurrently in a single pass. No manual parameter tuning or linguistic flagging is ever required from the end-user.

## 8. How to use:

### 8.1. GUI version

* Click the first Browse... button to select your target PDF file.
* (Optional) Click the second Browse... button to specify a custom destination path and filename. If left blank, it will automatically output to the same directory with the correct extension (.docx or .md).
* Click Convert. The integrated log window will display real-time progress updates.

### 8.2. Command Line Interface (CLI)

Ideal for scripting, scheduling, or keyboard-driven workflows.

* Convert PDF to Markdown (.md):
    
    ```bash
    python cli_to_md.py "path/to/document.pdf" ["optional/output/path.md"]
    ```

    (Supports wildcard patterns such as *.pdf for batch processing multiple documents).

* Convert PDF to Word (.docx):
    ```Bash
    python cli_to_docx.py "path/to/document.pdf" ["optional/output/path.docx"]
    ```
