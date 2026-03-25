from PyPDF2 import PdfReader

reader = PdfReader('input/payslips.pdf')
print(f'Total pages: {len(reader.pages)}')

for i, page in enumerate(reader.pages):
    text = page.extract_text()
    print(f'\n--- Page {i+1} ---')
    print(text[:300])
