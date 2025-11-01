from docx import Document

doc = Document("main/cit.docx")

for para in doc.paragraphs:
    for run in para.runs:
        size = run.font.size.pt if run.font.size else "inherited"
        print(f"Text: {run.text} | Size: {size}")