import fitz  # PyMuPDF
import tempfile

def extract_text_from_pdf(upload_file):
    """
    Extract text from uploaded CV PDF
    """

    # Save temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(upload_file.file.read())
        tmp_path = tmp.name

    # Open PDF
    doc = fitz.open(tmp_path)

    text = ""
    for page in doc:
        text += page.get_text()

    return text