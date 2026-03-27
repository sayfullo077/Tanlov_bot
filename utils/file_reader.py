from docx import Document
import PyPDF2

MAX_TEXT_LENGTH = 15000  # Limit (belgilar soni)


async def read_txt(file_path):
    encodings = ["utf-8", "utf-16", "latin1", "cp1251", "iso-8859-1"]

    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                text = f.read()
                return check_text_length(text)
        except UnicodeDecodeError:
            continue

    return "⚠️ Unable to decode text file. Unsupported encoding."


async def read_docx(file_path: str) -> str:
    doc = Document(file_path)
    text = "\n".join([p.text for p in doc.paragraphs])
    return check_text_length(text)


async def read_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return check_text_length(text)


def check_text_length(text: str) -> str:
    text = text.strip()
    if len(text) > MAX_TEXT_LENGTH:
        return f"⚠️ The file is too large.\nPlease send a shorter document (max ~{MAX_TEXT_LENGTH} characters)."
    if len(text) < 10:
        return "⚠️ The file does not contain enough readable text."
    return text


async def extract_text(file_path: str) -> str:
    """
    Fayl kengaytmasiga qarab matnni chiqaradi va limitni tekshiradi.
    """
    if file_path.endswith(".txt"):
        return await read_txt(file_path)
    elif file_path.endswith(".docx"):
        return await read_docx(file_path)
    elif file_path.endswith(".pdf"):
        return await read_pdf(file_path)
    else:
        return "⚠️ Unsupported file type."
