import glob
import json
import os
import re
import pdfplumber

# 各梯次試題與標準答案 PDF 的雲端檢視連結 (Google Drive View URL) 與本地相對路徑對照表
SOURCE_METADATA = {
    ("111", "01"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1Vr3xk-iPqzM6u4D8v9JE2iStVGQN8IFt/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1ei6-lxRseYdp6eiP9OIThTj_XDhVXdDe/view?usp=drivesdk",
        "exam_local_path": "downloads/11101.pdf",
        "answer_local_path": "downloads/11101a.pdf",
    },
    ("111", "02"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1xluxIQTeFxTIkORR8e0FjPPzw5mecGL_/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1CDQzQb6EyJ1qbULBV6odbCB88lSI8rl5/view?usp=drivesdk",
        "exam_local_path": "downloads/11102.pdf",
        "answer_local_path": "downloads/11102a.pdf",
    },
    ("111", "03"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1aU9fwwVVUDH5ye_l-PtJ87VLWlpYV5ep/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1hl3KVuL38xe5k6KhD_2zjJopHL_iM-eV/view?usp=drivesdk",
        "exam_local_path": "downloads/11103.pdf",
        "answer_local_path": "downloads/11103a.pdf",
    },
    ("112", "01"): {
        "exam_pdf_url": "https://drive.google.com/file/d/10AtrQE_FOb8VkUEanihrrF_rmjSUIrgg/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1mSwqgGpqV-amTcy06CsL0YWg1E_yIH-a/view?usp=drivesdk",
        "exam_local_path": "downloads/11201.pdf",
        "answer_local_path": "downloads/11201a.pdf",
    },
    ("112", "02"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1Aztw_we82oHx66WCJDEFsbyfCG2-nd2z/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1oSsjuzwGQHbZSDdqPKjfAJnXJu1AjhqW/view?usp=drivesdk",
        "exam_local_path": "downloads/11202.pdf",
        "answer_local_path": "downloads/11202a.pdf",
    },
    ("112", "03"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1yG_p1PcbVGa60__iCh_1b5WaINVHogEr/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1aD9ZAML_90Pc19KvhvmjGNBMIpz2g8qy/view?usp=drivesdk",
        "exam_local_path": "downloads/11203.pdf",
        "answer_local_path": "downloads/11203a.pdf",
    },
    ("113", "01"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1mQK20UDnlBQIgd-aueoUfs6-c5FvyFZb/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1ZN1a-Bk1Hz-s6iCdwnJq9_T7f7tpzJ4Z/view?usp=drivesdk",
        "exam_local_path": "downloads/11301.pdf",
        "answer_local_path": "downloads/11301a.pdf",
    },
    ("113", "02"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1QbOkZx1UtmQEpXGrClLURFKyorPO1qaD/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1gOqRpxg_Xzy5LrH2xEE_yDEHITKDRU_q/view?usp=drivesdk",
        "exam_local_path": "downloads/11302.pdf",
        "answer_local_path": "downloads/11302a.pdf",
    },
    ("113", "03"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1I0cKqW8EsHwUX2l6MSJzkY_8bz_1vVB0/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1BnMxppxW_UzMeA4_RhhIeCdjrQf-cvN6/view?usp=drivesdk",
        "exam_local_path": "downloads/11303.pdf",
        "answer_local_path": "downloads/11303a.pdf",
    },
    ("114", "01"): {
        "exam_pdf_url": "https://drive.google.com/file/d/19a8IHJ1xr49-3DqNU9E-0x4NE6iGdht9/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1Fb8yy2_OCFLRxSTNfL4aofGTivAgqz71/view?usp=drivesdk",
        "exam_local_path": "downloads/11401.pdf",
        "answer_local_path": "downloads/11401a.pdf",
    },
    ("114", "02"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1zScTw-v-MKjHUURGUc7lz7ti0kpYTOHX/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1bPnnOcoYvn4oNxvnZdiSYkdpydeQl4-E/view?usp=drivesdk",
        "exam_local_path": "downloads/11402.pdf",
        "answer_local_path": "downloads/11402a.pdf",
    },
    ("114", "03"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1DnYTzyXmvkege85ONhmbXJAajN-9__uu/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1700cU4Ow601WQlkaMeLS0NQ_UDi9ws_0/view?usp=drivesdk",
        "exam_local_path": "downloads/11403.pdf",
        "answer_local_path": "downloads/11403a.pdf",
    },
    ("115", "01"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1EItoE_qa27dp5mSJ3fKI2yyR2jHJJDah/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1uJHC9Nj-TxaNOC3VEQVlKUwEP2RFX46d/view?usp=drivesdk",
        "exam_local_path": "downloads/11501.pdf",
        "answer_local_path": "downloads/11501a.pdf",
    },
    ("115", "02"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1Pe6HmdTdnyEyz-h_Gw59hH41nCzFKVEB/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1J_Tx-q2se2FRNwSVVNeF7w1rs5wu-Mvg/view?usp=drivesdk",
        "exam_local_path": "downloads/11502.pdf",
        "answer_local_path": "downloads/11502a.pdf",
    },
    # 新增共同科目題庫（試題與解答合一）
    ("113", "FM"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1lFFoBIo7B-u1zPDjE_WRVsLoX-yqNvBq/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1lFFoBIo7B-u1zPDjE_WRVsLoX-yqNvBq/view?usp=drivesdk",
        "exam_local_path": "downloads/金融市場常識-113.pdf",
        "answer_local_path": "downloads/金融市場常識-113.pdf",
    },
    ("113", "ET"): {
        "exam_pdf_url": "https://drive.google.com/file/d/1TqfaYt6NXimNBKAeXdLIVQs9ECFra2Xg/view?usp=drivesdk",
        "answer_pdf_url": "https://drive.google.com/file/d/1TqfaYt6NXimNBKAeXdLIVQs9ECFra2Xg/view?usp=drivesdk",
        "exam_local_path": "downloads/職業道德-113.pdf",
        "answer_local_path": "downloads/職業道德-113.pdf",
    },
}

NUM_TO_LETTER = {"1": "A", "2": "B", "3": "C", "4": "D"}


def parse_year_session(filename: str, full_text: str):
    """從檔名或內文標題解析年度 (year) 與梯次/期別 (session, 2位數)。"""
    base = os.path.splitext(os.path.basename(filename))[0]

    m_short = re.match(r'^(1\d{2})(0[1-4])a?$', base, re.IGNORECASE)
    if m_short:
        return m_short.group(1), m_short.group(2)

    m = re.search(r'(1\d{2})\s*[Q\-_第]?\s*0?([1-4])\s*[次期]?', base, re.IGNORECASE)
    if m:
        return m.group(1), f"{int(m.group(2)):02d}"

    m_text = re.search(r'(1\d{2})\s*年\s*第\s*([1-4])\s*次', full_text)
    if m_text:
        return m_text.group(1), f"{int(m_text.group(2)):02d}"

    return "未知", "01"


def extract_pdf_text(pdf_path: str) -> str:
    """讀取 PDF 所有頁面文字並合併。"""
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t)
    return "\n".join(pages_text)


def extract_answers_from_text(full_text: str) -> dict:
    """從解答文字中解析「投信投顧相關法規（含自律規範）」科目的標準答案 (題號 1~50 -> A/B/C/D)。"""
    answers = {}
    ans_section_match = re.search(
        r'投信投顧相關法規[^\n]*(?:解答|標準答案)(.*?)(?:證券投資與財務分析|證券交易相關法規|\Z)',
        full_text,
        flags=re.DOTALL,
    )
    if not ans_section_match and re.search(r'(?:試題解答|標準答案|測驗試題解答)', full_text):
        ans_section_match = re.search(
            r'投信投顧相關法規(.*?)(?:證券投資與財務分析|證券交易相關法規|\Z)',
            full_text,
            flags=re.DOTALL,
        )
    if not ans_section_match:
        return answers

    target_text = ans_section_match.group(1)

    for m in re.finditer(r'(?<!\d)([1-9]|[1-4]\d|50)\s*[\.、:：]?\s*([A-D])(?![A-Za-z])', target_text):
        q_num = int(m.group(1))
        ans = m.group(2).upper()
        if 1 <= q_num <= 50 and q_num not in answers:
            answers[q_num] = ans

    if len(answers) < 50:
        lines = [line.strip() for line in target_text.splitlines() if line.strip()]
        for i in range(len(lines) - 1):
            nums = [int(x) for x in re.findall(r'(?<!\d)([1-9]|[1-4]\d|50)(?!\d)', lines[i])]
            opts = re.findall(r'(?<![A-Za-z])([A-D])(?![A-Za-z])', lines[i + 1])
            if len(nums) >= 5 and len(nums) == len(opts):
                for q_num, ans in zip(nums, opts):
                    answers[q_num] = ans

    return answers


def isolate_law_subject_region(full_text: str) -> str:
    """精準擷取「投信投顧相關法規」科目的題目區間，排除其他科目標題與末頁解答。"""
    start_match = re.search(r'專業科目\s*[：:]\s*投信投顧相關法規', full_text)
    region = full_text[start_match.start():] if start_match else full_text

    end_match = re.search(
        r'(?:\n\s*1\d{2}\s*年\s*第\s*\d+\s*次[^\n]*試題\s*\n\s*)?專業科目\s*[：:]\s*(?:證券投資與財務分析|證券交易相關法規)'
        r'|\n\s*1\d{2}\s*年\s*第\s*\d+\s*次[^\n]*試題解答'
        r'|投信投顧相關法規[^\n]*解答',
        region[20:],
    )
    if end_match:
        region = region[: 20 + end_match.start()]

    region = re.sub(r'\s*1\d{2}\s*年\s*第\s*\d+\s*次投信投顧業務[^\n]*\Z', '', region)
    return region


def extract_questions_from_text(full_text: str) -> list:
    """從試題內文解析「投信投顧相關法規」每題題號、題目內文與 A/B/C/D 選項。"""
    question_region = isolate_law_subject_region(full_text)

    first_q = re.search(r'(?:^|\n)\s*1\.\s*', question_region)
    if first_q:
        question_region = question_region[first_q.start():]

    pattern = re.compile(r'(?:^|\n)\s*([1-9]|[1-4]\d|50)\.\s*')
    matches = list(pattern.finditer(question_region))

    parsed_questions = []
    for idx, match in enumerate(matches):
        q_num = int(match.group(1))
        start_idx = match.end()
        end_idx = matches[idx + 1].start() if idx + 1 < len(matches) else len(question_region)
        block = question_region[start_idx:end_idx].strip()

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

        parsed_questions.append({
            "q_num": q_num,
            "question": q_stem,
            "options": options,
        })

    return parsed_questions


def process_question_pdf(question_pdf_path: str, answer_pdf_path: str = None) -> list:
    """解析單一「投信投顧相關法規」試題 PDF 檔案，結合對應標準答案與來源連結資訊。"""
    full_text = extract_pdf_text(question_pdf_path)
    year, session = parse_year_session(question_pdf_path, full_text)

    if answer_pdf_path and os.path.exists(answer_pdf_path):
        ans_text = extract_pdf_text(answer_pdf_path)
        answers = extract_answers_from_text(ans_text)
    else:
        answers = extract_answers_from_text(full_text)

    raw_questions = extract_questions_from_text(full_text)

    rel_exam_path = f"downloads/{os.path.basename(question_pdf_path)}"
    rel_ans_path = (
        f"downloads/{os.path.basename(answer_pdf_path)}"
        if answer_pdf_path
        else rel_exam_path
    )
    meta = SOURCE_METADATA.get((year, session), {})
    source_links = {
        "exam_pdf_url": meta.get("exam_pdf_url", rel_exam_path),
        "answer_pdf_url": meta.get("answer_pdf_url", rel_ans_path),
        "exam_local_path": meta.get("exam_local_path", rel_exam_path),
        "answer_local_path": meta.get("answer_local_path", rel_ans_path),
    }

    results = []
    for item in raw_questions:
        q_num = item["q_num"]
        results.append({
            "id": q_num,
            "year": year,
            "session": session,
            "subject": "投信投顧相關法規",
            "question": item["question"],
            "options": item["options"],
            "answer": answers.get(q_num, ""),
            "source_links": source_links,
        })
    return results


def process_sfi_bank_pdf(pdf_path: str, year: str, session_code: str, subject_name: str) -> list:
    """
    解析「金融市場常識-113」與「職業道德-113」題庫 PDF（格式：(答案1~4) 題號 題幹 (1)...(2)...(3)...(4)...）。
    自動將 (1)~(4) 對應轉為 A~D 標準格式並附上雲端與本地來源連結。
    """
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            cleaned_lines = []
            for line in t.splitlines():
                s = line.strip()
                if re.match(r'^Part\s+[I12V]+\s*[：:]', s, re.IGNORECASE):
                    continue
                if re.match(r'^答案\s+題號\s+題目', s):
                    continue
                if re.match(r'^\d{1,2}$', s):
                    continue
                cleaned_lines.append(line)
            pages_text.append("\n".join(cleaned_lines))

    full_text = "\n".join(pages_text)

    pattern = re.compile(r'(?:^|\n)\s*\(([1-4])\)\s+(\d{1,3})\s+')
    all_candidates = list(pattern.finditer(full_text))

    matches = []
    expected_q = 1
    for m in all_candidates:
        q_num = int(m.group(2))
        if q_num == expected_q:
            matches.append(m)
            expected_q += 1

    rel_path = f"downloads/{os.path.basename(pdf_path)}"
    meta = SOURCE_METADATA.get((year, session_code), {})
    source_links = {
        "exam_pdf_url": meta.get("exam_pdf_url", rel_path),
        "answer_pdf_url": meta.get("answer_pdf_url", rel_path),
        "exam_local_path": meta.get("exam_local_path", rel_path),
        "answer_local_path": meta.get("answer_local_path", rel_path),
    }

    results = []
    for idx, m in enumerate(matches):
        ans_num = m.group(1)
        q_num = int(m.group(2))
        start_idx = m.end()
        end_idx = matches[idx + 1].start() if idx + 1 < len(matches) else len(full_text)
        block = full_text[start_idx:end_idx].strip()

        opt_1_matches = list(re.finditer(r'\(1\)', block))
        chosen_split = None
        for m1 in reversed(opt_1_matches):
            sub = block[m1.start():]
            if re.search(r'\(1\).*?\(2\).*?\(3\).*?\(4\)', sub, flags=re.DOTALL):
                chosen_split = m1.start()
                break

        if chosen_split is None:
            continue

        q_stem = re.sub(r'\s*\n\s*', '', block[:chosen_split]).strip()
        opts_raw = block[chosen_split:].strip()

        opt_match = re.search(
            r'^\(1\)\s*(.*?)\s*\(2\)\s*(.*?)\s*\(3\)\s*(.*?)\s*\(4\)\s*(.*)\Z',
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

        results.append({
            "id": q_num,
            "year": year,
            "session": session_code,
            "subject": subject_name,
            "question": q_stem,
            "options": options,
            "answer": NUM_TO_LETTER.get(ans_num, ""),
            "source_links": source_links,
        })

    return results


def discover_downloaded_pdfs(download_dir: str) -> list:
    """探索 downloads/ 目錄下的 111–115 投信投顧法規試題 PDF。"""
    found = set(glob.glob(os.path.join(download_dir, "*.pdf")))
    for yr in range(104, 116):
        for sess in range(1, 5):
            for pattern in (
                f"{yr}{sess:02d}.pdf",
                f"{yr}{sess:02d}a.pdf",
                f"{yr}Q{sess}投信投顧相關法規（含自律規範）.pdf",
                f"{yr}Q{sess}投信投顧相關法規(含自律規範).pdf",
            ):
                p = os.path.join(download_dir, pattern)
                if os.path.exists(p):
                    found.add(p)
    return sorted(found)


def validate_questions(questions: list) -> dict:
    """檢查解析資料是否缺漏選項、缺少正確答案或缺少來源連結 (source_links)。"""
    missing_options = []
    missing_answers = []
    missing_sources = []
    for q in questions:
        opts = q.get("options", {})
        if any(k not in opts or not str(opts[k]).strip() for k in ("A", "B", "C", "D")):
            missing_options.append((q["subject"], q["year"], q["session"], q["id"]))
        if q.get("answer") not in ("A", "B", "C", "D"):
            missing_answers.append((q["subject"], q["year"], q["session"], q["id"]))
        src = q.get("source_links", {})
        if not src.get("exam_pdf_url") or not src.get("answer_pdf_url"):
            missing_sources.append((q["subject"], q["year"], q["session"], q["id"]))

    return {
        "total_count": len(questions),
        "missing_options_count": len(missing_options),
        "missing_answers_count": len(missing_answers),
        "missing_sources_count": len(missing_sources),
        "missing_options": missing_options,
        "missing_answers": missing_answers,
        "missing_sources": missing_sources,
    }


def main():
    download_dir = "/working_dir/c_139da38595e8b89e/downloads"
    all_pdfs = discover_downloaded_pdfs(download_dir)

    question_pdfs = [
        p for p in all_pdfs
        if re.match(r'^11[1-5]0[1-4]\.pdf$', os.path.basename(p), re.IGNORECASE)
    ]

    all_questions = []
    global_id = 1
    file_summaries = []

    # 1. 解析 111–115 年投信投顧相關法規（14 梯次，共 700 題）
    for q_pdf in question_pdfs:
        base_no_ext = os.path.splitext(q_pdf)[0]
        candidate_ans_pdf = f"{base_no_ext}a.pdf"
        has_ans_pdf = os.path.exists(candidate_ans_pdf)

        parsed = process_question_pdf(q_pdf, candidate_ans_pdf if has_ans_pdf else None)
        ans_found_count = sum(1 for q in parsed if q["answer"] in ("A", "B", "C", "D"))
        file_summaries.append({
            "subject": "投信投顧相關法規",
            "question_pdf": os.path.basename(q_pdf),
            "answer_pdf": os.path.basename(candidate_ans_pdf) if has_ans_pdf else "內嵌解答",
            "questions_extracted": len(parsed),
            "answers_matched": ans_found_count,
        })

        for q in parsed:
            q["id"] = global_id
            global_id += 1
            all_questions.append(q)

    # 2. 解析新增之兩份 113 年共同科目題庫：金融市場常識 (504題) 與 職業道德 (616題)
    extra_banks = [
        ("金融市場常識-113.pdf", "113", "FM", "金融市場常識"),
        ("職業道德-113.pdf", "113", "ET", "職業道德"),
    ]
    for filename, yr, sess_code, subj_name in extra_banks:
        pdf_path = os.path.join(download_dir, filename)
        if os.path.exists(pdf_path):
            parsed = process_sfi_bank_pdf(pdf_path, yr, sess_code, subj_name)
            ans_found_count = sum(1 for q in parsed if q["answer"] in ("A", "B", "C", "D"))
            file_summaries.append({
                "subject": subj_name,
                "question_pdf": filename,
                "answer_pdf": f"{filename} (題庫內附標準答案)",
                "questions_extracted": len(parsed),
                "answers_matched": ans_found_count,
            })
            for q in parsed:
                q["id"] = global_id
                global_id += 1
                all_questions.append(q)

    report = validate_questions(all_questions)

    output_paths = [
        "/working_dir/c_139da38595e8b89e/questions.json",
        "/working_dir/c_139da38595e8b89e/artifacts/file_generation/ttl=63d/output/questions.json",
    ]
    os.makedirs(os.path.dirname(output_paths[1]), exist_ok=True)
    for out_path in output_paths:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(all_questions, f, ensure_ascii=False, indent=2)

    print("=== 解析與驗證報告 ===")
    for s in file_summaries:
        print(
            f" - [{s['subject']}] 試題檔: {s['question_pdf']} | 解答檔: {s['answer_pdf']} | "
            f"提取題數: {s['questions_extracted']} | 成功配對答案數: {s['answers_matched']}"
        )
    print(f"總題數: {report['total_count']}")
    print(f"缺漏選項題數: {report['missing_options_count']}")
    print(f"缺少正確答案題數: {report['missing_answers_count']}")
    print(f"缺少來源連結題數: {report['missing_sources_count']}")


if __name__ == "__main__":
    main()
