import pdfplumber

# =========================
# PDF TEXT EXTRACTION
# =========================

def extract_pdf_text(uploaded_file):

    try:

        pdf_text = ""

        with pdfplumber.open(uploaded_file) as pdf:

            for page in pdf.pages:

                text = page.extract_text()

                if text:
                    pdf_text += text + "\n"

        return pdf_text[:5000]

    except Exception as e:

        print("PDF Error:", e)

        return ""

# =========================
# CHECK PDF TEXT
# =========================

def has_pdf_text(pdf_text):

    if not pdf_text:
        return False

    return bool(pdf_text.strip())