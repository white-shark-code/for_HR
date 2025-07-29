# Тестовые задания для HR

Этот репозиторий содержит реализацию тестового задания для позиции Backend-разработчика.

## 🛒 Проект: Бэкенд для скрапинга интернет-магазина

**Краткое описание:**  
Flask-приложение для автоматической синхронизации данных товаров из внешнего API с базой данных и предоставления информации через REST API.

**Основной стек:**  
Flask, PostgreSQL, Docker, Celery, Redis

### 🚀 Быстрый запуск
```bash
git clone https://github.com/white-shark-code/for_HR.git
cd for_HR/Noxer
cp .env.example .env  # настройте параметры при необходимости
docker-compose up -d
```

**Доступ к данным:**  
После запуска откройте в браузере:  
http://localhost:5555/info

[Полное техническое задание](https://github.com/white-shark-code/for_HR/blob/main/Noxer/TechnicalTask.md)
