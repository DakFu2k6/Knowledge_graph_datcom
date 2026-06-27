import pandas as pd
import numpy as np

def extract_esco_hierarchy(input_path, output_path):
    print("Bước 1: Đang tải dữ liệu skillsHierarchy_en.csv")
    cols_to_use = [
        'Level 0 URI', 'Level 0 preferred term',
        'Level 1 URI', 'Level 1 preferred term',
        'Level 2 URI', 'Level 2 preferred term',
        'Level 3 URI', 'Level 3 preferred term'
    ]
    df = pd.read_csv(input_path, usecols=cols_to_use)
    df = df.replace({np.nan: None})
    edges = []
    print("Bước 2: Đang trích xuất các cạnh phân cấp")
    for _, row in df.iterrows():
        if row['Level 1 URI'] and row['Level 0 URI']:
            edges.append({
                'child_uri': row['Level 1 URI'],
                'child_label': row['Level 1 preferred term'],
                'parent_uri': row['Level 0 URI'],
                'parent_label': row['Level 0 preferred term']
            })
        if row['Level 2 URI'] and row['Level 1 URI']:
            edges.append({
                'child_uri': row['Level 2 URI'],
                'child_label': row['Level 2 preferred term'],
                'parent_uri': row['Level 1 URI'],
                'parent_label': row['Level 1 preferred term']
            })
        if row['Level 3 URI'] and row['Level 2 URI']:
            edges.append({
                'child_uri': row['Level 3 URI'],
                'child_label': row['Level 3 preferred term'],
                'parent_uri': row['Level 2 URI'],
                'parent_label': row['Level 2 preferred term']
            })
    edges_df = pd.DataFrame(edges)
    print(f"Tổng số cạnh thô trích xuất được: {len(edges_df)}")
    print("Bước 3: Đang xử lý làm sạch và lọc trùng trùng lặp")
    edges_df = edges_df.drop_duplicates().reset_index(drop=True)
    for col in ['child_label', 'parent_label']:
        edges_df[col] = edges_df[col].astype(str).str.strip()
    print(f"Tổng số cạnh phân cấp duy nhất (Unique Edges): {len(edges_df)}")
    print(f"Bước 4: Đang lưu kết quả thành phẩm vào: {output_path}")
    edges_df.to_csv(output_path, index=False, encoding='utf-8')
    print("Hoàn thành.")

if __name__ == "__main__":
    INPUT_FILE = r"C:\Users\Admin\Downloads\SkillGraph\ESCO dataset - v1.2.0 - classification - en - csv\skillsHierarchy_en.csv"
    OUTPUT_FILE = r"C:\Users\Admin\Downloads\SkillGraph\outputs\is_a_subskill_of.csv"
    extract_esco_hierarchy(INPUT_FILE, OUTPUT_FILE)