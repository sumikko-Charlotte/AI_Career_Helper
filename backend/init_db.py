import os
import csv

def init_database():
    # 1. 创建 data 文件夹
    if not os.path.exists("data"):
        os.makedirs("data")
        print("✅ 创建 data 文件夹成功")

    # 2. 创建 users.csv (如果不存在)
    csv_path = "data/users.csv"
    if not os.path.exists(csv_path):
        headers = ["username", "password", "grade", "target_role"]
        # 初始化一个 admin 账号
        initial_data = [
            {"username": "admin", "password": "123456", "grade": "管理员", "target_role": "系统管理"},
            {"username": "test", "password": "123", "grade": "大三", "target_role": "Java开发"}
        ]
        
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(initial_data)
        print("✅ 创建 users.csv 成功 (已包含 admin/123456)")
    else:
        print("⚠️ users.csv 已存在，跳过创建")

if __name__ == "__main__":
    init_database()