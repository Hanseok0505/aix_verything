import os, subprocess, sys

def open_in_explorer(path: str) -> bool:
    """파일이 있는 폴더를 열고 파일을 선택합니다."""
    try:
        # 경로 정규화 (Windows 백슬래시 유지)
        # 경로가 상대 경로일 수 있으므로 abspath 사용
        if not os.path.isabs(path):
            # 상대 경로인 경우 현재 작업 디렉토리 기준으로 변환
            path = os.path.abspath(path)
        else:
            path = os.path.normpath(path)
        
        if not os.path.exists(path):
            print(f"[File Ops] Path does not exist: {path}")
            return False
    except Exception as e:
        print(f"[File Ops] Path normalization error: {e}")
        return False
    
    try:
        if sys.platform.startswith("win"):
            if os.path.isfile(path):
                # Windows: explorer.exe /select 옵션 사용
                # 경로에 공백이나 특수문자가 있어도 처리되도록 여러 방법 시도
                
                # 방법 1: subprocess.Popen 사용 (리스트 형식, shell=False)
                # Windows에서 가장 안정적인 방법
                try:
                    print(f"[File Ops] Opening folder for file: {path}")
                    # /select 다음에 쉼표 필요 (Windows 표준 형식)
                    # 경로를 raw string으로 처리하여 백슬래시 문제 방지
                    proc = subprocess.Popen(
                        ["explorer.exe", "/select,", path],
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                    # 프로세스가 시작되면 성공으로 간주 (explorer.exe는 즉시 반환됨)
                    # 잠시 대기하여 프로세스가 정상 시작되었는지 확인
                    import time
                    time.sleep(0.1)
                    if proc.poll() is None or proc.returncode == 0:
                        return True
                    else:
                        print(f"[File Ops] Process exited with code: {proc.returncode}")
                except Exception as e1:
                    print(f"[File Ops] Method 1 (Popen) failed: {e1}")
                    import traceback
                    traceback.print_exc()
                
                # 방법 2: shell=True 사용 (경로에 특수문자가 있을 때)
                try:
                    # 경로를 따옴표로 감싸서 전달
                    # 백슬래시는 그대로 유지, 따옴표만 이스케이프
                    escaped_path = path.replace('"', '""')  # 따옴표만 이스케이프
                    # /select, 형식 사용
                    cmd = f'explorer.exe /select,"{escaped_path}"'
                    print(f"[File Ops] Trying shell command: {cmd}")
                    proc = subprocess.Popen(
                        cmd,
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                    return True
                except Exception as e2:
                    print(f"[File Ops] Method 2 (shell) failed: {e2}")
                
                # 방법 3: 폴더 경로만 열기 (최후의 수단)
                try:
                    folder_path = os.path.dirname(path)
                    print(f"[File Ops] Opening folder only: {folder_path}")
                    subprocess.Popen(
                        ["explorer.exe", folder_path],
                        shell=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    return True
                except Exception as e3:
                    print(f"[File Ops] Method 3 (folder only) failed: {e3}")
                    return False
            else:
                # 폴더인 경우
                print(f"[File Ops] Opening folder: {path}")
                subprocess.Popen(
                    ["explorer.exe", path],
                    shell=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True
        if sys.platform == "darwin":
            if os.path.isfile(path):
                subprocess.Popen(["open", "-R", path])
            else:
                subprocess.Popen(["open", path])
            return True
        subprocess.Popen(["xdg-open", path])
        return True
    except Exception as e:
        try:
            error_msg = f"[File Ops] Error opening in explorer: {e}"
            print(error_msg.encode('utf-8', errors='replace').decode('utf-8'))
        except:
            print(f"[File Ops] Error opening in explorer: {str(e)}")
        return False

def open_file(path: str) -> bool:
    """파일을 기본 애플리케이션으로 직접 엽니다."""
    try:
        # 경로 정규화 (Windows 백슬래시 유지)
        # 경로가 상대 경로일 수 있으므로 abspath 사용
        if not os.path.isabs(path):
            # 상대 경로인 경우 현재 작업 디렉토리 기준으로 변환
            path = os.path.abspath(path)
        else:
            path = os.path.normpath(path)
        
        if not os.path.exists(path):
            print(f"[File Ops] File not found: {path}")
            return False
    except Exception as e:
        print(f"[File Ops] Path normalization error: {e}")
        return False
    
    try:
        if sys.platform.startswith("win"):
            # Windows: os.startfile 사용 (가장 안정적, 한국어 경로 지원)
            # os.startfile은 Windows API를 직접 사용하므로 인코딩 문제 없음
            if os.path.isfile(path):
                print(f"[File Ops] Opening file: {path}")
                try:
                    os.startfile(path)
                    return True
                except Exception as e1:
                    print(f"[File Ops] os.startfile failed: {e1}")
                    # 대체 방법: subprocess 사용
                    try:
                        subprocess.Popen(
                            ["cmd", "/c", "start", "", path],
                            shell=False,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        return True
                    except Exception as e2:
                        print(f"[File Ops] cmd start failed: {e2}")
                        return False
            else:
                # 폴더인 경우
                print(f"[File Ops] Opening folder: {path}")
                subprocess.Popen(
                    ["explorer.exe", path],
                    shell=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True
        if sys.platform == "darwin":
            subprocess.Popen(["open", path])
            return True
        subprocess.Popen(["xdg-open", path])
        return True
    except Exception as e:
        try:
            error_msg = f"[File Ops] Error opening file: {e}"
            print(error_msg.encode('utf-8', errors='replace').decode('utf-8'))
        except:
            print(f"[File Ops] Error opening file: {str(e)}")
        return False
