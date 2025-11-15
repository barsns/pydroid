#!/bin/bash
cd /storage/emulated/0/pydroid/pydroid
echo "Синхронизация: $(date +'%H:%M:%S')"
git pull origin main
git add .
if git status --porcelain | grep .; then
  git commit -m "Авто: $(date +'%H:%M')"
fi
git push origin main
echo "ГОТОВО!"
