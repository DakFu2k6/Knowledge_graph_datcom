import pandas as pd
import ast
from rapidfuzz import process, fuzz
import os

def run_entity_alignment(esco_skills_path, extracted_kg_path, output_path):
    print("Bước 1: Đang tải từ điển kỹ năng chuẩn ESCO")
    df_esco = pd.read_csv(esco_skills_path, usecols=['conceptUri', 'preferredLabel'])
    df_esco = df_esco.dropna(subset=['preferredLabel'])
    esco_dict = {}
    for _, row in df_esco.iterrows():
        label_clean = str(row['preferredLabel']).strip()
        esco_dict[label_clean.lower()] = {
            'original_label': label_clean,
            'uri': row['conceptUri']
        }
    esco_lowercase_list = list(esco_dict.keys())
    print(f" Đã nạp {len(esco_lowercase_list)} kỹ năng chuẩn từ ESCO vào từ điển.")
    print("Bước 2: Đang thu thập extracted skills từ dữ liệu tuyển dụng")
    df_extracted = pd.read_csv(extracted_kg_path, usecols=['extracted_flat'])
    df_extracted = df_extracted.dropna(subset=['extracted_flat'])
    raw_skills_set = set()
    for _, row in df_extracted.iterrows():
        try:
            skills_list = ast.literal_eval(row['extracted_flat'])
            for s in skills_list:
                if s:
                    raw_skills_set.add(str(s).strip().lower())
        except (ValueError, SyntaxError):
            continue         
    raw_skills_list = sorted(list(raw_skills_set))
    print(f" Tìm thấy {len(raw_skills_list)} kỹ năng thô độc nhất (Unique Raw Skills) cần map.")
    print("Bước 3: Đang tiến hành Fuzzy Matching (Entity Alignment)")
    alignment_results = []
    total_skills = len(raw_skills_list)
    for idx, raw_skill in enumerate(raw_skills_list):
        match_result = process.extractOne(raw_skill, esco_lowercase_list, scorer=fuzz.WRatio)
        if match_result:
            best_match_lower, score, _ = match_result
            esco_info = esco_dict[best_match_lower]
            alignment_results.append({
                'raw_skill': raw_skill,
                'esco_preferred_label': esco_info['original_label'],
                'esco_uri': esco_info['uri'],
                'confidence_score': round(score, 2)
            })
        else:
            alignment_results.append({
                'raw_skill': raw_skill,
                'esco_preferred_label': None,
                'esco_uri': None,
                'confidence_score': 0.0
            })
        if (idx + 1) % 100 == 0 or (idx + 1) == total_skills:
            print(f" Đã xử lý: {idx + 1}/{total_skills} kỹ năng thô...")
    results_df = pd.DataFrame(alignment_results)
    results_df = results_df.sort_values(by='confidence_score', ascending=False).reset_index(drop=True)
    print("Bước 4: Đang thống kê tỷ lệ Mapping")
    mapped_count = len(results_df[results_df['confidence_score'] >= 80.0])
    print(f" Số lượng kỹ năng khớp mạnh (Score >= 80): {mapped_count}/{total_skills} ({round(mapped_count/total_skills*100, 2)}%)")
    print(f"Bước 5; Đang lưu kết quả thành phẩm vào: {output_path}")
    results_df.to_csv(output_path, index=False, encoding='utf-8')
    print(" Hoàn thành.")

if __name__ == "__main__":
    ESCO_SKILLS_FILE = r"C:\Users\Admin\Downloads\SkillGraph\ESCO dataset - v1.2.0 - classification - en - csv\skills_en.csv"
    EXTRACTED_KG_FILE = "extracted_kg_skills.csv"
    OUTPUT_FILE = r"C:\Users\Admin\Downloads\SkillGraph\outputs\entity_alignment_results.csv"
    if os.path.exists(ESCO_SKILLS_FILE) and os.path.exists(EXTRACTED_KG_FILE):
        run_entity_alignment(ESCO_SKILLS_FILE, EXTRACTED_KG_FILE, OUTPUT_FILE)
    else:
        print("Lỗi!")