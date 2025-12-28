"""별도 프로세스로 폴더 선택 대화상자 실행"""
import sys
import tkinter as tk
from tkinter import filedialog

try:
    # 루트 윈도우 생성 (숨김)
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    # 폴더 선택
    folder_path = filedialog.askdirectory(
        title="인덱싱할 폴더를 선택하세요",
        mustexist=True
    )
    
    if folder_path:
        print(folder_path)
    else:
        print("CANCELLED")
    
    root.destroy()
    sys.exit(0)
    
except Exception as e:
    print(f"ERROR: {str(e)}", file=sys.stderr)
    sys.exit(1)


