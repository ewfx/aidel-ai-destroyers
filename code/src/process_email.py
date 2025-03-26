import os
import fitz  # PyMuPDF
from email import policy
from email.parser import BytesParser
from docx import Document

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def process_eml_file(eml_path):
    with open(eml_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    # Extract email content
    email_content = msg.get_body(preferencelist=('plain', 'html')).get_content()

    # Extract attachments
    attachments = []
    for part in msg.iter_attachments():
        content_type = part.get_content_type()
        filename = part.get_filename()
        if content_type == 'application/pdf':
            with open(filename, 'wb') as file:
                file.write(part.get_payload(decode=True))
            attachments.append((filename, 'pdf'))
        elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            with open(filename, 'wb') as file:
                file.write(part.get_payload(decode=True))
            attachments.append((filename, 'docx'))
        elif content_type == 'message/rfc822':
            with open(filename, 'wb') as file:
                file.write(part.get_payload(decode=True))
            attachments.append((filename, 'eml'))

    # Extract text from attachments
    attachment_texts = {}
    for filename, filetype in attachments:
        if filetype == 'pdf':
            attachment_texts[filename] = extract_text_from_pdf(filename)
        elif filetype == 'docx':
            attachment_texts[filename] = extract_text_from_docx(filename)
        elif filetype == 'eml':
            nested_email_content, nested_attachments = process_eml_file(filename)
            attachment_texts[filename] = nested_email_content
            attachment_texts.update(nested_attachments)
        os.remove(filename)  # Remove the file after processing

    content = "Email Content:\n" + email_content
    for filename, text in attachment_texts.items():
        content += f"\nText from {filename}:\n" + text

    return content
