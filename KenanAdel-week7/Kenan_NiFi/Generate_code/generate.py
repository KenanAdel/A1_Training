import os
import json
import time
import random
from datetime import datetime

OUTPUT_DIR = r"D:\nifi_input\data"
current_id = 1000
file_count = 0

def generate_messy_data(is_duplicate=False, duplicate_record=None):
    global current_id
    
    if is_duplicate and duplicate_record:
        return duplicate_record

    current_id += 1
    clean_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "id": current_id,
        "user_id": random.randint(1, 5),
        "amount": random.choice([150.50, 200.75, "missing", None]),
        "timestamp": clean_timestamp,
        "category": random.choice(["Tech", "Food", "Fashion"]),
        "status": random.choice(["Active", "Not_Active", None, "???"])
    }

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f" Started! Generating INTRA-FILE duplicates every 3rd file...")

    while True:
        try:
            file_count += 1
            file_name = f"batch_{int(time.time())}.json"
            file_path = os.path.join(OUTPUT_DIR, file_name)
            
            records = []
            num_new_records = random.randint(2, 4)
            
            for _ in range(num_new_records):
                records.append(generate_messy_data())

            if file_count % 3 == 0:
                target_to_dup = random.choice(records)
                records.append(generate_messy_data(is_duplicate=True, duplicate_record=target_to_dup))
                print(f" Added an INTRA-FILE DUPLICATE (ID: {target_to_dup['id']}) to {file_name}")

            with open(file_path, 'w') as f:
                json.dump(records, f, indent=4)
            
            print(f" Created: {file_name} ({len(records)} records)")
            time.sleep(5)
            
        except Exception as e:
            print(f" Error: {e}")
            time.sleep(2)