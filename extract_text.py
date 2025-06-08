import os
import fitz  # PyMuPDF
from pathlib import Path

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("parsed_text")

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text() for page in doc])
    return text

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for pdf_file in UPLOAD_DIR.glob("*.pdf"):
        output_file = OUTPUT_DIR / f"{pdf_file.stem}.txt"
        if not output_file.exists():
            print(f"Extracting text from {pdf_file}...")
            text = extract_text_from_pdf(pdf_file)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Saved to {output_file}")
        else:
            print(f"Skipped {pdf_file}, already processed.")

if __name__ == "__main__":
    main()
