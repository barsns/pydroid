#!/usr/bin/env python3
import os
import subprocess
import datetime

# ПУТЬ К GIT В PYDROID 3
GIT_PATH = "/data/data/ru.iiec.pydroid3/files/usr/bin/git"
REPO_DIR = "/storage/emulated/0/pydroid/pydroid"

os.chdir(REPO_DIR)

def run_git(cmd):
    try:
        full_cmd = [GIT_PATH] + cmd.split()
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Ошибка: {e}"

print("СИНХРОНИЗАЦИЯ С GITHUB")
print(f"Время: {datetime.datetime.now().strftime('%H:%M:%S')}")

# 1. Pull
print("\nЗагружаем с GitHub...")
print(run_git("pull origin main"))

# 2. Проверяем изменения
status = run_git("status --porcelain")
if not status.strip():
    print("Нет новых файлов.")
else:
    print(f"Найдено изменений: {len(status.splitlines())}")
    print("Добавляем...")
    print(run_git("add ."))
    
    msg = f"Авто: {datetime.datetime.now().strftime('%d.%m %H:%M')}"
    print(f"Коммит: {msg}")
    commit_result = run_git(f'commit -m "{msg}"')
    print(commit_result)
    
    print("Отправляем на GitHub...")
    push_result = run_git("push origin main")
    print(push_result)

print("\nГОТОВО! Файлы на GitHub.")