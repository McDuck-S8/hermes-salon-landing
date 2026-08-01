#!/bin/bash
# FreeDeepseekAPI heartbeat — проверяет что сервер жив, перезапускает если упал
FREE_ROOT="D:/Portable_Soft/FreeDeepseekAPI"
PORT=9655

# Check if responding
curl -sf --connect-timeout 5 "http://127.0.0.1:$PORT/v1/models" > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "[$(date)] FreeDeepseekAPI DOWN на порту $PORT — перезапускаю..."
  # Kill any stale node processes on that port
  lsof -ti tcp:$PORT 2>/dev/null | xargs kill 2>/dev/null
  sleep 1
  # Start
  env NON_INTERACTIVE=1 node "$FREE_ROOT/server.js" &
  echo "[$(date)] FreeDeepseekAPI RESTARTED (PID: $!)"
  # Quick check
  sleep 3
  curl -sf --connect-timeout 5 "http://127.0.0.1:$PORT/v1/models" > /dev/null && \
    echo "[$(date)] OK — отвечает" || \
    echo "[$(date)] FAIL — не отвечает после перезапуска"
else
  # Silent exit — всё хорошо, не беспокоим
  exit 0
fi
