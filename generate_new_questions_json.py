import os
import sys
import re
import json
import pdfplumber

sys.stdout.reconfigure(encoding='utf-8')

TARGET_DIR = r"H:\國泰投信\投信投顧業務員10401-11502"
IMAGE_ANS_PATH = r"scratch\image_answers.json"
OUT_JSON = r"new_1100_questions.json"

with open(IMAGE_ANS_PATH, "r", encoding="utf-8") as f:
    IMAGE_ANSWERS = json.load(f)

SESSIONS_CONFIG = [
    {"year": "105", "session": "02", "file": r"105\105Q2投信投顧相關法規.pdf", "ans_type": "text_full"},
    {"year": "105", "session": "03", "file": r"105\105Q3投信投顧相關法規（含自律規範）.pdf", "ans_type": "text_full"},
    {"year": "105", "session": "04", "file": r"105\Q4投顧業務員-投信投顧相關法規.pdf", "ans_type": "text_full"},
    {"year": "106", "session": "01", "file": r"106\投信投顧相關法規（含自律規範）.pdf", "ans_type": "text_full"},
    {"year": "106", "session": "02", "file": r"106\投信投顧相關法規（含自律規範）Download File (99).pdf", "ans_type": "text_full"},
    {"year": "106", "session": "03", "file": r"106\106年投信投顧業務員_Q3信投顧相關法規(含自律規範).pdf", "ans_type": "image_answers"},
    {"year": "106", "session": "04", "file": r"106\投信投顧業務員_Q4信投顧相關法規(含自律規範)_題答.pdf", "ans_type": "image_answers"},
    {"year": "107", "session": "01", "file": r"107\(投信投顧) 107年Q1信投顧相關法規(含自律規範).pdf", "ans_type": "image_answers"},
    {"year": "107", "session": "02", "file": r"107\[投信投顧] Q2投信投顧相關法規(含自律規範).pdf", "ans_type": "image_answers"},
    {"year": "107", "session": "03", "file": r"107\107年Q3投信投顧相關法規(含自律規範).pdf", "ans_type": "image_answers"},
    {"year": "107", "session": "04", "file": r"107\107年 投信投顧業務員_Q4投信投顧相關法規(含自律規範).pdf", "ans_type": "image_answers"},
    {"year": "108", "session": "01", "file": r"108\108年投信投顧商業務員_Q1投信投顧相關法規(含自律規範).pdf", "ans_type": "image_answers"},
    {"year": "108", "session": "02", "file": r"108\108年Q2投信投顧相關法規(含自律規範)-投信投顧.pdf", "ans_type": "image_answers"},
    {"year": "108", "session": "03", "file": r"108\Q3投信投顧相關法規(含自律規範)_108年投信投顧業務員.pdf", "ans_type": "image_answers"},
    {"year": "108", "session": "04", "file": r"108\Q4投信投顧相關法規(含自律規範)-108年投信投顧業務員.pdf", "ans_type": "image_answers"},
    {"year": "109", "session": "01", "file": r"109\Q1投信投顧相關法規(含自律規範)-109年投信投顧業務員.pdf", "ans_type": "image_answers"},
    {"year": "109", "session": "02", "file": r"109\Q2投信投顧相關法規(含自律規範)-109年投信投顧業務員.pdf", "ans_type": "image_answers"},
    {"year": "109", "session": "03", "file": r"109\10903.pdf", "ans_file": r"109\10903a.pdf", "ans_type": "separate_file"},
    {"year": "109", "session": "04", "file": r"109\10904.pdf", "ans_file": r"109\10904a.pdf", "ans_type": "separate_file"},
    {"year": "110", "session": "01", "file": r"110\11001.pdf", "ans_file": r"110\11001a.pdf", "ans_type": "separate_file"},
    {"year": "110", "session": "02", "file": r"110\11002.pdf", "ans_file": r"110\11002a.pdf", "ans_type": "separate_file"},
    {"year": "110", "session": "03", "file": r"110\11003.pdf", "ans_file": r"110\11003a.pdf", "ans_type": "separate_file"},
]

def extract_answers_from_text(text: str) -> dict:
    answers = {}
    m = re.search(r'投信投顧相關法規[^\n]*(?:解答|標準答案)(.*?)(?:證券|期貨|\Z)', text, re.DOTALL)
    target = m.group(1) if m else text
    
    matches = re.finditer(r'(?<!\d)([1-9]|[1-4]\d|50)\s*[\.、:：]?\s*([A-D])(?![A-Za-z])', target)
    for match in matches:
        q_num = int(match.group(1))
        ans = match.group(2).upper()
        if 1 <= q_num <= 50 and q_num not in answers:
            answers[q_num] = ans
            
    all_credit = re.finditer(r'(?<!\d)([1-9]|[1-4]\d|50)\s*均給分', target)
    for match in all_credit:
        q_num = int(match.group(1))
        if 1 <= q_num <= 50 and q_num not in answers:
            answers[q_num] = "A"
    return answers

def extract_questions_from_pdf(pdf_path: str):
    with pdfplumber.open(pdf_path) as pdf:
        pages_text = [p.extract_text() or "" for p in pdf.pages]
        
    full_text = "\n".join(pages_text)
    
    start_match = re.search(r'專業科目\s*[：:]\s*(?:投信投顧相關法規|信投顧相關法規)', full_text)
    region = full_text[start_match.start():] if start_match else full_text
    
    end_match = re.search(
        r'(?:\n\s*1\d{2}\s*年\s*第\s*\d+\s*次[^\n]*試題\s*\n\s*)?專業科目\s*[：:]\s*(?:證券投資與財務分析|證券交易相關法規)'
        r'|\n\s*1\d{2}\s*年\s*第\s*\d+\s*次[^\n]*試題解答'
        r'|投信投顧相關法規[^\n]*解答',
        region[20:],
    )
    if end_match:
        region = region[:20 + end_match.start()]
        
    first_q = re.search(r'(?:^|\n)\s*1\.\s*', region)
    if first_q:
        region = region[first_q.start():]
        
    pattern = re.compile(r'(?:^|\n)\s*([1-9]|[1-4]\d|50)\.\s*')
    matches = list(pattern.finditer(region))
    
    parsed = {}
    for idx, match in enumerate(matches):
        q_num = int(match.group(1))
        start_idx = match.end()
        end_idx = matches[idx + 1].start() if idx + 1 < len(matches) else len(region)
        block = region[start_idx:end_idx].strip()
        
        block = re.sub(r'(?<=\s)([A-D])\)', r'(\1)', block)
        
        opt_a_matches = list(re.finditer(r'\(A\)', block))
        if not opt_a_matches:
            continue
            
        chosen_split = None
        for m_a in opt_a_matches:
            sub = block[m_a.start():]
            if re.search(r'\(A\).*?\(B\).*?\(C\).*?\(D\)', sub, flags=re.DOTALL):
                chosen_split = m_a.start()
                break
                
        if chosen_split is None:
            for m_a in opt_a_matches:
                sub = block[m_a.start():]
                if re.search(r'\(A\).*?\(B\).*?\(C\).*?\(C\)', sub, flags=re.DOTALL):
                    c_matches = list(re.finditer(r'\(C\)', sub))
                    if len(c_matches) >= 2:
                        second_c = m_a.start() + c_matches[1].start()
                        block = block[:second_c] + "(D)" + block[second_c+3:]
                        chosen_split = m_a.start()
                        break
                    
        if chosen_split is None:
            continue
            
        q_stem_raw = block[:chosen_split].strip()
        opts_raw = block[chosen_split:].strip()
        
        q_stem = re.sub(r'\s*\n\s*', '', q_stem_raw).strip()
        
        opt_match = re.search(
            r'^\(A\)\s*(.*?)\s*\(B\)\s*(.*?)\s*\(C\)\s*(.*?)\s*\(D\)\s*(.*)\Z',
            opts_raw,
            flags=re.DOTALL,
        )
        if not opt_match:
            continue
            
        options = {
            "A": re.sub(r'\s*\n\s*', '', opt_match.group(1)).strip(),
            "B": re.sub(r'\s*\n\s*', '', opt_match.group(2)).strip(),
            "C": re.sub(r'\s*\n\s*', '', opt_match.group(3)).strip(),
            "D": re.sub(r'\s*\n\s*', '', opt_match.group(4)).strip(),
        }
        
        parsed[q_num] = {
            "question": q_stem,
            "options": options
        }
        
    return parsed

def main():
    current_id = 1821
    new_questions = []
    
    for cfg in SESSIONS_CONFIG:
        year = cfg['year']
        session = cfg['session']
        session_key = f"{year}-{session}"
        fpath = os.path.join(TARGET_DIR, cfg['file'])
        
        questions = extract_questions_from_pdf(fpath)
        
        answers = {}
        if cfg['ans_type'] == "image_answers":
            raw = IMAGE_ANSWERS.get(session_key, {})
            answers = {int(k): v for k, v in raw.items()}
        elif cfg['ans_type'] == "text_full":
            with pdfplumber.open(fpath) as pdf:
                full_txt = "\n".join([p.extract_text() or "" for p in pdf.pages])
                answers = extract_answers_from_text(full_txt)
        elif cfg['ans_type'] == "separate_file":
            ans_path = os.path.join(TARGET_DIR, cfg['ans_file'])
            with pdfplumber.open(ans_path) as pdf:
                ans_txt = "\n".join([p.extract_text() or "" for p in pdf.pages])
                answers = extract_answers_from_text(ans_txt)
                
        assert len(questions) == 50, f"Error: session {session_key} has {len(questions)} questions!"
        assert len(answers) == 50, f"Error: session {session_key} has {len(answers)} answers!"
        
        local_exam = f"downloads/{year}{session}.pdf"
        local_ans = f"downloads/{year}{session}a.pdf"
        
        for q_num in range(1, 51):
            q_info = questions[q_num]
            ans = answers[q_num]
            
            item = {
                "id": current_id,
                "year": year,
                "session": session,
                "subject": "投信投顧相關法規",
                "question": q_info["question"],
                "options": q_info["options"],
                "answer": ans,
                "source_links": {
                    "exam_pdf_url": local_exam,
                    "answer_pdf_url": local_ans,
                    "exam_local_path": local_exam,
                    "answer_local_path": local_ans
                },
                "hint": "",
                "explanation": "",
                "explanation_last_edited_by": "系統標準解答"
            }
            new_questions.append(item)
            current_id += 1
            
    print(f"Generated {len(new_questions)} new questions (ID 1821 to {current_id - 1})")
    
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(new_questions, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved to {OUT_JSON}")

if __name__ == "__main__":
    main()
