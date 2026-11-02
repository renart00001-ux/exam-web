import os
import sys
import json
import urllib.request
import time
import concurrent.futures
from threading import Lock

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "gemini-3.8-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

INPUT_FILE = "new_1100_questions.json"
OUTPUT_FILE = "law_1100_extras.json"
BATCH_SIZE = 10
MAX_WORKERS = 2

PROMPT_TEMPLATE = """你是一位專業的金融證照考試題目解析助理。接下來我會提供一系列考試題目（包含題目、選項與標準答案），請你為每一道題目生成「提示」與「解析」，並嚴格遵守以下格式與原則：

### 1. 提示原則 (Hint)
- 篇幅限制：嚴格限制在 1～2 句話以內，力求簡短俐落。
- 內容風格：點到為止的暗示或常理推論。
  - 暗示錯誤選項不可能的原因、正確選項的正面性，或揪出語意破綻（如「忽視」、「無須同意」、「絕對」、「隨意」等極端詞）。
  - 若法規數字偏多，可用原則暗示（例如：「既然是『總』代理，窗口通常只有一個」、「數字通常挑影響力極低的比例」）。
  - 若題目過於直接，可用簡短常理引導（例如：「本題可用常理判斷，牽涉公共利益者標準通常最嚴」）。
  - 嚴格禁令：不得直接爆雷指出答案字母（例如不得寫「答案選 C」或「請選 D」）。

### 2. 解析原則 (Explanation)
- 四選項完整覆蓋：每個選項（A、B、C、D）各用精準的一句話直擊重點。
- 清楚標示屬性：每一行開頭**必須嚴格固定標註 `（正確）` 或 `（錯誤）`**（不要寫成「非本題正確答案」或「本題正確答案」，只能寫「（正確）」或「（錯誤）」）。
- 直擊痛點：明確說明錯誤選項的法規破綻、數字陷阱或邏輯矛盾，或說明正確選項之法規依據與規範目的。
- 排版格式：固定採 Markdown 條列式，每選項一行：
  * **A（正確/錯誤）**：[一句話直擊重點]
  * **B（正確/錯誤）**：[一句話直擊重點]
  * **C（正確/錯誤）**：[一句話直擊重點]
  * **D（正確/錯誤）**：[一句話直擊重點]

請為以下題目生成提示與解析，並以純 JSON 陣列輸出，每個物件包含：
- "id": 題目編號 (整數)
- "hint": 提示內容（最多兩句話）
- "explanation": 解析內容（A、B、C、D 各一行，格式為：* **A（正確/錯誤）**：說明。\\n* **B（正確/錯誤）**：說明。\\n* **C（正確/錯誤）**：說明。\\n* **D（正確/錯誤）**：說明。）

題目列表：
{questions_text}

請務必只輸出純 JSON 陣列（以 [ 開頭，以 ] 結尾），不要包含 markdown 代碼標籤或任何其他說明文字。
"""

lock = Lock()

def load_existing():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_result(batch_results):
    with lock:
        current = load_existing()
        for item in batch_results:
            current[str(item["id"])] = {
                "id": item["id"],
                "hint": item.get("hint", "").strip(),
                "explanation": item.get("explanation", "").strip()
            }
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
        print(f"[Progress] Saved {len(current)} / 1100 questions...", flush=True)

def process_batch(batch, retry_count=3):
    q_text = []
    for q in batch:
        q_text.append(f"""ID: {q['id']}
題目：{q['question']}
選項：
A: {q['options']['A']}
B: {q['options']['B']}
C: {q['options']['C']}
D: {q['options']['D']}
標準答案：{q['answer']}
""")
    prompt = PROMPT_TEMPLATE.format(questions_text="\n---\n".join(q_text))
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }
    
    for attempt in range(retry_count):
        try:
            req = urllib.request.Request(
                URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                raw_text = res["candidates"][0]["content"]["parts"][0]["text"].strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()
                
                batch_res = json.loads(raw_text)
                save_result(batch_res)
                return True
        except Exception as e:
            print(f"Error on attempt {attempt+1} for batch {[q['id'] for q in batch]}: {e}", flush=True)
            time.sleep(2 * (attempt + 1))
            
    print(f"Failed batch after {retry_count} attempts: {[q['id'] for q in batch]}", flush=True)
    return False

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.", flush=True)
        return
        
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        all_questions = json.load(f)
        
    existing = load_existing()
    pending = [q for q in all_questions if str(q["id"]) not in existing]
    
    print(f"Total questions: {len(all_questions)}", flush=True)
    print(f"Already completed: {len(existing)}", flush=True)
    print(f"Pending to generate: {len(pending)}", flush=True)
    
    if not pending:
        print("All questions already generated!", flush=True)
        return
        
    batches = [pending[i:i + BATCH_SIZE] for i in range(0, len(pending), BATCH_SIZE)]
    print(f"Total batches to process: {len(batches)}", flush=True)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_batch, b) for b in batches]
        concurrent.futures.wait(futures)
        
    final_count = len(load_existing())
    print(f"\nBatch generation completed. Total in {OUTPUT_FILE}: {final_count} / {len(all_questions)}", flush=True)

if __name__ == "__main__":
    main()
