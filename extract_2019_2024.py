import fitz
import glob
import re

results = []

for year in range(2019, 2025):
    for pdf_file in sorted(glob.glob(f'prs/*{year}*.pdf')):
        try:
            doc = fitz.open(pdf_file)
            text = ''
            for page in doc:
                text += page.get_text()
            
            # Special case for Yes bank accelerated exclusion
            if 'YES BANK' in text.upper() and 'NIFTY 50' in text.upper():
                 pass # we'll catch it or handle it separately if needed
            
            if re.search(r'nifty\s*50(?!0)', text, re.I) and ('exclude' in text.lower() or 'include' in text.lower() or 'replace' in text.lower()):
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                for i, line in enumerate(lines):
                    if re.match(r'^\d+\)?\s*NIFTY\s*50(?!0)', line, re.I) or line == 'NIFTY 50' or line == 'NIFTY 50 Index' or line == 'Nifty 50':
                        
                        date_ctx = ''
                        for j in range(max(0, i-15), i):
                            if 'effective' in lines[j].lower() or 'close of' in lines[j].lower() or 'date' in lines[j].lower():
                                date_ctx += lines[j] + ' '
                        
                        snippet = ''
                        for j in range(i, min(i+25, len(lines))):
                            if j > i and (re.match(r'^\d+\)?\s*NIFTY', lines[j], re.I) or lines[j].startswith('About India Index') or lines[j].startswith('About NSE Indices')):
                                break
                            snippet += lines[j] + '\n'
                        
                        results.append({
                            'file': pdf_file,
                            'date_ctx': date_ctx.strip(),
                            'snippet': snippet.strip()
                        })
                        break
        except Exception as e:
            pass

with open('extracted_changes.txt', 'w', encoding='utf-8') as f:
    for r in results:
        f.write(f'\n========== {r["file"]} ==========\n')
        f.write(f'DATE CTX: {r["date_ctx"]}\n')
        f.write(f'{r["snippet"]}\n')
