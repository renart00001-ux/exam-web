import os
import shutil
from PIL import Image

TARGET_DIR = r"H:\國泰投信\投信投顧業務員10401-11502"
DOWNLOADS_DIR = r"downloads"
ANSWERS_IMG_DIR = r"scratch\answers"

os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# 22 sessions mapping to standard names: YYYSS.pdf and YYYSSa.pdf
SESSIONS = [
    ("10502", r"105\105Q2投信投顧相關法規.pdf", "self"),
    ("10503", r"105\105Q3投信投顧相關法規（含自律規範）.pdf", "self"),
    ("10504", r"105\Q4投顧業務員-投信投顧相關法規.pdf", "self"),
    ("10601", r"106\投信投顧相關法規（含自律規範）.pdf", "self"),
    ("10602", r"106\投信投顧相關法規（含自律規範）Download File (99).pdf", "self"),
    ("10603", r"106\106年投信投顧業務員_Q3信投顧相關法規(含自律規範).pdf", "106_03.png"),
    ("10604", r"106\投信投顧業務員_Q4信投顧相關法規(含自律規範)_題答.pdf", "106_04.png"),
    ("10701", r"107\(投信投顧) 107年Q1信投顧相關法規(含自律規範).pdf", "107_01.png"),
    ("10702", r"107\[投信投顧] Q2投信投顧相關法規(含自律規範).pdf", "107_02.png"),
    ("10703", r"107\107年Q3投信投顧相關法規(含自律規範).pdf", "107_03.png"),
    ("10704", r"107\107年 投信投顧業務員_Q4投信投顧相關法規(含自律規範).pdf", "107_04.png"),
    ("10801", r"108\108年投信投顧商業務員_Q1投信投顧相關法規(含自律規範).pdf", "108_01.png"),
    ("10802", r"108\108年Q2投信投顧相關法規(含自律規範)-投信投顧.pdf", "108_02.png"),
    ("10803", r"108\Q3投信投顧相關法規(含自律規範)_108年投信投顧業務員.pdf", "108_03.png"),
    ("10804", r"108\Q4投信投顧相關法規(含自律規範)-108年投信投顧業務員.pdf", "108_04.png"),
    ("10901", r"109\Q1投信投顧相關法規(含自律規範)-109年投信投顧業務員.pdf", "109_01.png"),
    ("10902", r"109\Q2投信投顧相關法規(含自律規範)-109年投信投顧業務員.pdf", "109_02.png"),
    ("10903", r"109\10903.pdf", r"109\10903a.pdf"),
    ("10904", r"109\10904.pdf", r"109\10904a.pdf"),
    ("11001", r"110\11001.pdf", r"110\11001a.pdf"),
    ("11002", r"110\11002.pdf", r"110\11002a.pdf"),
    ("11003", r"110\11003.pdf", r"110\11003a.pdf"),
]

def main():
    for code, exam_rel, ans_source in SESSIONS:
        # Copy exam PDF
        exam_src = os.path.join(TARGET_DIR, exam_rel)
        exam_dst = os.path.join(DOWNLOADS_DIR, f"{code}.pdf")
        shutil.copy2(exam_src, exam_dst)
        print(f"Copied {exam_dst}")
        
        # Prepare answer PDF
        ans_dst = os.path.join(DOWNLOADS_DIR, f"{code}a.pdf")
        if ans_source == "self":
            # The answer is already in the last page of exam PDF
            shutil.copy2(exam_src, ans_dst)
            print(f"Copied {ans_dst} (from self)")
        elif ans_source.endswith(".png"):
            # Convert cropped table image or page image to clean 1-page PDF
            img_path = os.path.join(ANSWERS_IMG_DIR, ans_source)
            im = Image.open(img_path)
            im_rgb = im.convert("RGB")
            im_rgb.save(ans_dst, "PDF", resolution=150)
            print(f"Generated {ans_dst} (from {ans_source})")
        else:
            # Separate file in source directory
            ans_src = os.path.join(TARGET_DIR, ans_source)
            shutil.copy2(ans_src, ans_dst)
            print(f"Copied {ans_dst} (from {ans_source})")

if __name__ == "__main__":
    main()
