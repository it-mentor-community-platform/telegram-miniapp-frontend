# Telegram Mini App Frontend

Frontend-сервис для раздачи статических файлов Telegram Mini App.

---

## 🧠 Контекст

Сервис предназначен раздачи frontend-части Telegram Mini App.  
Используется как точка входа для пользовательского интерфейса и взаимодействия с Telegram Web Apps API.

---

## ⚙️ Технологический стек

- HTML / CSS / JavaScript
- **nginx** 
- **Docker**

---

## 🔄 Взаимодействие

Сервис:

- Раздаёт статические файлы через HTTP
- Может выполнять HTTP-запросы к backend-сервисам в рамках логики клиентского приложения
- Работает в составе общей микросервисной архитектуры проекта

---

## ▶️ Запуск сервиса локально

### Сборка Docker-образа

```bash
docker build -t telegram-miniapp-frontend:local .
```
### Запуск контейнера
```bash
docker run --rm -p 80:80 telegram-miniapp-frontend:local
```