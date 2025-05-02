## System Setup

- **Tesseract OCR** (system installation):
  - **Ubuntu/Debian**: `sudo apt install tesseract-ocr`
  - **macOS** (Homebrew): `brew install tesseract`
  - **Windows**:
    1. Download the Windows installer from the [Tesseract Releases](https://github.com/tesseract-ocr/tesseract/releases) page.
    2. Run the installer (default install path `C:\Program Files\Tesseract-OCR`).
    3. Add the install directory to your PATH:
       - Open **System Properties** → **Environment Variables**.
       - Under **System variables**, select **Path** → **Edit** → **New** and paste the install folder.
       - Click **OK** on all dialogs, then reopen your terminal/IDE.
    4. Verify with:
       ```bash
       tesseract --version
       ```

- **FFmpeg** (CLI tool for audio extraction):
  - **Ubuntu/Debian**: `sudo apt install ffmpeg`
  - **macOS** (Homebrew): `brew install ffmpeg`
  - **Windows**:
    1. Download the static build from [FFmpeg Download](https://ffmpeg.org/download.html).
    2. Extract and add the `bin` folder to your PATH as above.
    3. Verify with:
       ```bash
       ffmpeg -version
       ```

**Optional:** If you cannot edit your PATH, set the `TESSERACT_CMD` environment variable to point directly to the Tesseract executable. For example:

```bash
export TESSERACT_CMD="C:/Program Files/Tesseract-OCR/tesseract.exe"
