#!/usr/bin/env python3
import os
import subprocess
import datetime

REPO_DIR = "/storage/emulated/0/pydroid/pydroid"
os.chdir(REPO_DIR)

def run(cmd):
    return subprocess.getoutput(cmd)

print(f"Синхронизация: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 1. Pull с GitHub
print("Загружаем изменения с GitHub...")
pull = run("git pull origin main")
print(pull)

# 2. Добавляем все изменения
print("Добавляем файлы...")
add = run("git add .")
print("Изменения найдены.")

# 3. Коммит (если есть что)
status = run("git status --porcelain")
if status.strip():
    msg = f"Авто-синхронизация {datetime.datetime.now().strftime('%H:%M')}"
    commit = run(f'git commit -m "{msg}"')
    print(commit)
else:
    print("Нет изменений для коммита.")

# 4. Push на GitHub
print("Отправляем на GitHub...")
push = run("git push origin main")
print(push)

print("Синхронизация завершена!")