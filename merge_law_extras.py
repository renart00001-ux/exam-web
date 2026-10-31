import json
import re
import os

QUESTIONS_FILE = "questions.json"
EXTRAS_FILE = "law_700_extras.json"
INDEX_FILE = "index.html"

def main():
    if not os.path.exists(EXTRAS_FILE):
        print(f"Error: {EXTRAS_FILE} does not exist.")
        return
    
    with open(EXTRAS_FILE, "r", encoding="utf-8") as f:
        extras = json.load(f)
    print(f"Loaded {len(extras)} extras from {EXTRAS_FILE}")
    
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)
    print(f"Loaded {len(questions)} questions from {QUESTIONS_FILE}")
    
    updated_count = 0
    for q in questions:
        qid_str = str(q.get("id"))
        if qid_str in extras:
            extra = extras[qid_str]
            q["hint"] = extra.get("hint", "")
            q["explanation"] = extra.get("explanation", "")
            q["explanation_last_edited_by"] = "系統標準解答"
            updated_count += 1
            
    print(f"Updated {updated_count} questions with hints and explanations.")
    
    # 1. 儲存更新後的 questions.json
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved {QUESTIONS_FILE}")
    
    # 2. 同步更新 index.html 中的 EMBEDDED_QUESTIONS 常數 (使用精準字串切片避免 regex 轉義 \n 造成 JS 語法錯誤)
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    
    embedded_json_str = json.dumps(questions, ensure_ascii=False)
    
    start_marker = "const EMBEDDED_QUESTIONS = ["
    idx = html.find(start_marker)
    if idx != -1:
        end_idx = html.find("];", idx)
        if end_idx != -1:
            end_idx += 2
            new_html = html[:idx] + f"const EMBEDDED_QUESTIONS = {embedded_json_str};" + html[end_idx:]
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                f.write(new_html)
            print("Successfully updated EMBEDDED_QUESTIONS in index.html!")
        else:
            print("Warning: could not find end of EMBEDDED_QUESTIONS in index.html!")
    else:
        print("Warning: could not find start of EMBEDDED_QUESTIONS in index.html!")

if __name__ == "__main__":
    main()
