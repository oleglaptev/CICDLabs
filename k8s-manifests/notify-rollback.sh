#!/bin/bash
# lab-4/k8s-manifests/notify-rollback.sh

NOTIFICATION_FILE="notification.txt"

echo "Запуск canary-развёртывания с образом :broken..."
kubectl argo rollouts set image myapp myapp=localhost:5001/myapp:broken -n staging

echo "Ожидание завершения rollout (таймаут 600 секунд)..."
if ! kubectl argo rollouts status myapp -n staging --timeout 600s; then
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    MESSAGE="[$TIMESTAMP] Rollout myapp был автоматически откачен — доля ошибок 5xx превысила порог"
    echo "$MESSAGE" > "$NOTIFICATION_FILE"
    echo ""
    echo "ОТКАТ ЗАФИКСИРОВАН! Содержимое $NOTIFICATION_FILE:"
    cat "$NOTIFICATION_FILE"
    exit 1
else
    echo "Rollout завершён успешно"
    exit 0
fi