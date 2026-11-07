# -*- coding: utf-8 -*-
"""
Merge 1,100 new questions into questions.json and index.html,
updating UI badges, total question counts, 36 sessions, and v2.0.0 timeline.
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ORIGINAL_QUESTIONS_FILE = "questions.json"
NEW_QUESTIONS_FILE = "new_1100_questions.json"
EXTRAS_FILE = "law_1100_extras.json"
INDEX_FILE = "index.html"

ALL_36_LAW_SESSIONS = [
    {"code": "115-02", "label": "115年第02次（50題）"},
    {"code": "115-01", "label": "115年第01次（50題）"},
    {"code": "114-03", "label": "114年第03次（50題）"},
    {"code": "114-02", "label": "114年第02次（50題）"},
    {"code": "114-01", "label": "114年第01次（50題）"},
    {"code": "113-03", "label": "113年第03次（50題）"},
    {"code": "113-02", "label": "113年第02次（50題）"},
    {"code": "113-01", "label": "113年第01次（50題）"},
    {"code": "112-03", "label": "112年第03次（50題）"},
    {"code": "112-02", "label": "112年第02次（50題）"},
    {"code": "112-01", "label": "112年第01次（50題）"},
    {"code": "111-03", "label": "111年第03次（50題）"},
    {"code": "111-02", "label": "111年第02次（50題）"},
    {"code": "111-01", "label": "111年第01次（50題）"},
    {"code": "110-03", "label": "110年第03次（50題）"},
    {"code": "110-02", "label": "110年第02次（50題）"},
    {"code": "110-01", "label": "110年第01次（50題）"},
    {"code": "109-04", "label": "109年第04次（50題）"},
    {"code": "109-03", "label": "109年第03次（50題）"},
    {"code": "109-02", "label": "109年第02次（50題）"},
    {"code": "109-01", "label": "109年第01次（50題）"},
    {"code": "108-04", "label": "108年第04次（50題）"},
    {"code": "108-03", "label": "108年第03次（50題）"},
    {"code": "108-02", "label": "108年第02次（50題）"},
    {"code": "108-01", "label": "108年第01次（50題）"},
    {"code": "107-04", "label": "107年第04次（50題）"},
    {"code": "107-03", "label": "107年第03次（50題）"},
    {"code": "107-02", "label": "107年第02次（50題）"},
    {"code": "107-01", "label": "107年第01次（50題）"},
    {"code": "106-04", "label": "106年第04次（50題）"},
    {"code": "106-03", "label": "106年第03次（50題）"},
    {"code": "106-02", "label": "106年第02次（50題）"},
    {"code": "106-01", "label": "106年第01次（50題）"},
    {"code": "105-04", "label": "105年第04次（50題）"},
    {"code": "105-03", "label": "105年第03次（50題）"},
    {"code": "105-02", "label": "105年第02次（50題）"},
]

V2_TIMELINE_NODE = """        <!-- Node 0: v2.0.0 -->
        <div class="relative group">
          <div class="absolute -left-[31px] sm:-left-[39px] top-0.5 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs shadow-md ring-4 ring-indigo-100 font-bold">
            🚀
          </div>
          <div class="bg-indigo-50/50 border border-indigo-200/80 rounded-xl p-4 sm:p-5 transition hover:shadow-sm">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="px-2.5 py-0.5 rounded-md text-xs font-bold bg-indigo-600 text-white shadow-xs">v2.0.0</span>
                <span class="text-xs font-bold text-slate-500">2026-11-03</span>
                <span class="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">當前最新里程碑 / 法規考古題全面擴展至 105–115 年 36 梯次</span>
              </div>
              <span class="text-[11px] font-mono text-slate-400">commit: 81afef3</span>
            </div>
            <h3 class="text-sm sm:text-base font-bold text-slate-900 mb-2">
              題庫重大升級！納入 105–110 年 22 梯次法規考古題，全題庫躍升至 2,920 題，全面完成去識別化與 AI 標準提示/四選項解析
            </h3>
            <div class="flex flex-wrap gap-1.5 mb-3">
              <span class="px-2 py-0.5 rounded text-[11px] font-medium bg-white border border-indigo-200 text-indigo-800">📚 法規擴充至 36 梯次 1,800 題</span>
              <span class="px-2 py-0.5 rounded text-[11px] font-medium bg-white border border-emerald-200 text-emerald-700">🛡️ 徹底去識別化為公開版本</span>
              <span class="px-2 py-0.5 rounded text-[11px] font-medium bg-white border border-amber-200 text-amber-800">💡 1,100 題標準提示與解析全量上線</span>
              <span class="px-2 py-0.5 rounded text-[11px] font-medium bg-white border border-slate-200 text-slate-700">📄 44 份官方試題解答 PDF 入庫</span>
            </div>
            <ul class="text-xs sm:text-sm text-slate-600 space-y-1.5 list-disc list-inside leading-relaxed">
              <li><strong>📚 考科精準篩選與擴充</strong>：完整收錄 105 年 Q2～Q4、106 年 Q1～Q4、107 年 Q1～Q4、108 年 Q1～Q4、109 年 Q1～Q4、110 年 Q1～Q3 共 22 個新梯次 1,100 題「投信投顧相關法規（含自律規範）」考題，總題庫由 1,820 題擴增至 2,920 題（法規由 700 題增至 1,800 題）。嚴格排除其他非目標考科。</li>
              <li><strong>🛡️ 100% 徹底去識別化</strong>：所有題目題幹、選項與 PDF 均徹底清洗私人筆記、作者暱稱與水印雜訊，完全呈現為純淨合規的公開官方題庫。</li>
              <li><strong>💡 嚴格遵循標準 Prompt 提示與解析</strong>：針對新增之 1,100 題，全面依據 <code>PROMPT_STANDARD.md</code> 提供 1~2 句不爆雷直覺提示，以及四個選項（A/B/C/D）各一句直擊痛點的精準法規解析，標註（正確）/（錯誤）。</li>
              <li><strong>🎛️ 測驗引擎無縫連動</strong>：多選選單自動擴充為 36 梯次自由複選，支援隨機抽題與全量 2,920 題馬拉松出題，各梯次 PDF 試題與答案卡皆已就緒。</li>
            </ul>
          </div>
        </div>

"""

def main():
    with open(ORIGINAL_QUESTIONS_FILE, "r", encoding="utf-8") as f:
        orig_questions = json.load(f)
    print(f"Loaded original {len(orig_questions)} questions.")
    
    # Baseline 1820 questions (ID 1-1820)
    orig_1820 = [q for q in orig_questions if q["id"] <= 1820]
    print(f"Filtered to baseline 1,820 questions (ID 1-1820).")
    
    with open(NEW_QUESTIONS_FILE, "r", encoding="utf-8") as f:
        new_questions = json.load(f)
    print(f"Loaded {len(new_questions)} new questions (ID 1821-2920).")
    
    with open(EXTRAS_FILE, "r", encoding="utf-8") as f:
        extras = json.load(f)
    print(f"Loaded {len(extras)} AI hints/explanations from {EXTRAS_FILE}")
    
    # Merge extras into new questions
    extras_applied = 0
    for q in new_questions:
        qid_str = str(q["id"])
        if qid_str in extras:
            extra = extras[qid_str]
            q["hint"] = extra.get("hint", "").strip()
            q["explanation"] = extra.get("explanation", "").strip()
            q["explanation_last_edited_by"] = "系統標準解答"
            extras_applied += 1
            
    print(f"Applied {extras_applied} / {len(new_questions)} hints and explanations.")
    if extras_applied != len(new_questions):
        print(f"Error: expected {len(new_questions)} extras applied, but got {extras_applied}!")
        return
        
    full_questions = orig_1820 + new_questions
    print(f"Combined total: {len(full_questions)} questions.")
    
    # 1. Save updated questions.json
    with open(ORIGINAL_QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(full_questions, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved {ORIGINAL_QUESTIONS_FILE} ({len(full_questions)} questions).")
    
    # 2. Update index.html
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()
        
    # A. Update LAW_SESSIONS array
    law_sessions_json = json.dumps(ALL_36_LAW_SESSIONS, ensure_ascii=False, indent=8)
    start_law = html.find("const LAW_SESSIONS = [")
    if start_law != -1:
        end_law = html.find("];", start_law)
        if end_law != -1:
            end_law += 2
            html = html[:start_law] + f"const LAW_SESSIONS = {law_sessions_json};" + html[end_law:]
            print("Successfully updated LAW_SESSIONS array in index.html!")
        else:
            print("Warning: could not find end of LAW_SESSIONS")
    else:
        print("Warning: could not find start of LAW_SESSIONS")
            
    # B. Update UI counts and text
    html = html.replace("共 700 題", "共 1,800 題（36 梯次）")
    html = html.replace("111–115年共 14 梯次", "105–115年共 36 梯次")
    html = html.replace("111–115年歷屆", "105–115年歷屆")
    html = html.replace("14 個梯次核取方塊", "36 個梯次核取方塊")
    html = html.replace("14 梯次自由複選", "36 梯次自由複選")
    html = html.replace("支援 50 至 1,820 題", "支援 50 至 2,920 題")
    html = html.replace("全體 1,820 題", "全體 2,920 題")
    html = html.replace("總題數達 1,820 題", "總題數達 2,920 題")
    html = html.replace("整合成 1,820 題完整題庫", "整合成 2,920 題完整題庫")
    html = html.replace("題庫總量：<strong class=\"font-bold\">1,820 題</strong>", "題庫總量：<strong class=\"font-bold\">2,920 題</strong>")
    
    # C. Update version timeline in index.html
    html = html.replace("最新版本 v1.9.1", "最新版本 v2.0.0")
    html = html.replace("當前最新版本 / 修正 Google 登入無反應問題", "修正 Google 登入無反應問題")
    
    node1_marker = "<!-- Node 1: v1.9.1 -->"
    if node1_marker in html and "<!-- Node 0: v2.0.0 -->" not in html:
        html = html.replace(node1_marker, V2_TIMELINE_NODE + node1_marker)
        print("Successfully added v2.0.0 node to version timeline in index.html!")
        
    # D. Update EMBEDDED_QUESTIONS
    embedded_json_str = json.dumps(full_questions, ensure_ascii=False)
    start_q = html.find("const EMBEDDED_QUESTIONS = [")
    if start_q != -1:
        end_q = html.find("];", start_q)
        if end_q != -1:
            end_q += 2
            html = html[:start_q] + f"const EMBEDDED_QUESTIONS = {embedded_json_str};" + html[end_q:]
            print("Successfully updated EMBEDDED_QUESTIONS in index.html!")
        else:
            print("Warning: could not find end of EMBEDDED_QUESTIONS")
    else:
        print("Warning: could not find start of EMBEDDED_QUESTIONS")
        
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print("Successfully saved updated index.html!")

if __name__ == "__main__":
    main()
