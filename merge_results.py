import json
import glob
import re
import os

def extract_json_from_text(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None

def main():
    results_dir = "results"
    output_file = "final_results.json"
    
    files = sorted(glob.glob(os.path.join(results_dir, "*.json")))
    

    combined_data = []
    
    print(f"Найдено файлов: {len(files)}")
    
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        data = extract_json_from_text(content)
        
        if data:
            combined_data.append(data)


    if combined_data:

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
            
        print(f"Всего экспериментов: {len(combined_data)}")
        
        if os.path.exists("plot_results.py"):
            import subprocess
            subprocess.run(["python", "plot_results.py"])

if __name__ == "__main__":
    main()