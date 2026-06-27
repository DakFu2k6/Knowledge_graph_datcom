import pandas as pd
from itertools import combinations
from collections import Counter
import ast
import os

def build_compliment_edges(input_path, output_path):
    print("Bước 1: Đang tải và kiểm tra dữ liệu all_job_post")
    df = pd.read_csv(input_path, usecols=['job_id', 'job_skill_set'])
    df = df.dropna(subset=['job_skill_set'])
    skill_pairs_counter = Counter()
    print("Bước 2: Đang bóc tách chuỗi list và đếm các cặp kỹ năng đồng xuất hiện")
    total_rows = len(df)
    for idx, row in df.iterrows():
        try:
            skills_raw = ast.literal_eval(row['job_skill_set'])
            skills = sorted(list(set([str(s).strip().lower() for s in skills_raw if s])))
            if len(skills) >= 2:
                pairs = combinations(skills, 2)
                skill_pairs_counter.update(pairs)      
        except (ValueError, SyntaxError):
            continue
        if (idx + 1) % 5000 == 0 or (idx + 1) == total_rows:
            print(f" Đã xử lý: {idx + 1}/{total_rows} dòng tuyển dụng...")
    print("Bước 3: Đang định hình cấu trúc DataFrame đầu ra")
    output_data = []
    for (skill1, skill2), count in skill_pairs_counter.items():
        output_data.append({
            'skill1': skill1,
            'skill2': skill2,
            'count': count
        })  
    edges_df = pd.DataFrame(output_data)
    edges_df = edges_df.sort_values(by='count', ascending=False).reset_index(drop=True)
    print(f"Tổng số cặp kỹ năng đồng xuất hiện duy nhất tìm thấy: {len(edges_df)}")
    print(f"Bước 4: Đang lưu kết quả vào: {output_path}")
    edges_df.to_csv(output_path, index=False, encoding='utf-8')
    print(" Hoàn thành.")

if __name__ == "__main__":
    INPUT_FILE = "all_job_post.csv" 
    OUTPUT_FILE = r"C:\Users\Admin\Downloads\SkillGraph\outputs\compliment_edges.csv"
    if os.path.exists(INPUT_FILE):
        build_compliment_edges(INPUT_FILE, OUTPUT_FILE)
    else:
        print(f"Lỗi!")