# Jaeger в Minikube с сервисами

## Описание

Развертывание Jaeger в Minikube с двумя сервисами, которые:

1. Взаимодействуют между собой
2. Отправляют трейсы в Jaeger

## Требования

- Minikube
- kubectl
- Docker

## Установка

### 1. Запуск Minikube

```bash
minikube start --addons=ingress 
```

Ingress нужен для вызовов

### 2. Установка cert-manager

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml
```

### 3. Развертывание Jaeger

```bash
kubectl create namespace observability

kubectl apply -f k8s/jaeger-operator.yaml -n observability
kubectl get pods -n observability
//kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.51.0/jaeger-operator.yaml -n observability

kubectl apply -f k8s/jaeger-instance.yaml -n observability
```

### 4. Сборка и деплой сервисов

```bash
# Сборка образов
minikube image build -t service-a:latest services/service-a/
minikube image build -t service-b:latest services/service-b/

# Развертывание
kubectl apply -f k8s/services.yaml
```

## Проверка работы

### Доступ к Jaeger UI

```bash
# Проброс порта до Jaeger UI
kubectl port-forward svc/simplest-query 16686:16686
```

Откройте в браузере: http://localhost:16686

### Тестирование сервисов

```bash
# Вызов service-a, который вызывает service-b
# kubectl exec -it $(kubectl get pods -l app=service-a -o jsonpath='{.items[0].metadata.name}') -- wget -qO- http://service-a:8080
kubectl logs -l app=service-a --tail=20
# ИЛИ Если нет wget или curl. Используйте Python (гарантированно работает)
kubectl exec -it $(kubectl get pods -l app=service-a -o jsonpath='{.items[0].metadata.name}') -- python -c "import urllib.request; print(urllib.request.urlopen('http://service-a:8080/order').read().decode())"

# ИЛИ Пробросьте порт и вызовите локально (удобнее для отладки)
# В одном терминале
kubectl port-forward svc/service-a 8080:8080

# В другом терминале
curl http://localhost:8080/order

# ИЛИ Добавьте wget в образ (для будущих сборок) в Dockerfile
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
```

### Применение изменений

```bash
# Примените обновлённый манифест
kubectl apply -f k8s/services.yaml

# Перезапустите поды
kubectl rollout restart deployment/service-a
kubectl rollout restart deployment/service-b

# Проверьте, что переменные появились
kubectl describe pod -l app=service-a | grep -A2 "Environment:"
kubectl describe pod -l app=service-b | grep -A2 "Environment:"
```

## Структура проекта

- `services/service-a/` - Исходный код service-a
- `services/service-b/` - Исходный код service-b
- `k8s/services.yaml` - Конфигурация Kubernetes для сервисов
- `jaeger-instance.yaml` - Конфигурация Jaeger
