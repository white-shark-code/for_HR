### Тестовое задание: Backend для интернет-магазина  
**Используемые технологии**: Flask, Docker, PostgreSQL, SQLAlchemy, Alembic, Celery, Redis, Gunicorn, Nginx  

---

### 🚀 Быстрый запуск  
1. Склонируйте репозиторий:  
   ```bash  
   git clone https://github.com/white-shark-code/for_HR.git
   cd Noxer  
   ```  
2. Копируйте `.env.example` и измените его под себя
   ```bash  
   cp .env.example .env
   vim .env
   ```  
2. Запустите приложение:  
   ```bash  
   docker-compose up -d
   ```  
3. Приложение будет доступно:  
   - **URL**: `http://localhost:5555/info`

---

### ⚙️ Конфигурация  
Настройки через переменные окружения (файл `.env`):  
```ini  
# Type database
DB_TYPE = "postgresql" # "sqlite" "mysql" "mariadb"

# Connection string
DB_PATH = "user:password@localhost:5432/dbname"
# Example for sqlite
# DB_PATH = "/./test.db"
# Example for MySQL/MariaDB
# DB_PATH = "user:password@localhost:3306/dbname"
# PostgreSQL (example for asyncpg driver)

# Every count hours task schedule
UPDATE_HOURS = 2

REDIS_URL = 'redis://localhost:6379/0'
```  

---

### 🗃️ Структура базы данных
**Основные таблицы**:

- **products**: Товары (`id`, `name`, `on_main`, `created_at`, `updated_at`)  
- **categories**: Категории (`id`, `name`, `image_url`, `sort_order`)  
- **tags**: Теги (`id`, `name` уникальный)  
- **product_marks**: Метки товаров (`id`, `name`)  
- **images**: Изображения (`id`, `image_url`, `main_image`, `title`, `product_id`)  
- **parameters**: Параметры (`id`, `price`, `old_price`, `name`, `parameter_string`, `product_id`)  
- **colors**: Цвета (`id`, `name`, `code`, `image_url`, `product_id`)  
- **reviews**: Отзывы (`id`, `image_url`, `product_id`)  

**Ассоциативные таблицы**:  
- **product_category_association**: Связь товар-категория (`product_id`, `category_id`)  
- **product_tag_association**: Связь товар-тег (`product_id`, `tag_id`)  
- **product_mark_association**: Связь товар-метка (`product_id`, `mark_id`)  

**Специальные таблицы**:  
- **extras**: Доп. характеристики (`id`, `characteristics`, `delivery`, `product_id`)  
- **excluded_items**: Исключения (`id`, `color_id`, `parameter_id`, `product_id`)  

---

### 🔗 Ключевые связи
| Отношение                | Тип           | Каскадное удаление               |
|--------------------------|---------------|----------------------------------|
| Товар → Изображения      | Один-ко-многим | ✅ (удаление изображений)         |
| Товар → Категории        | Многие-ко-многим | ❌ (только разрыв связи)          |
| Товар → Параметры        | Один-ко-многим | ✅ (удаление параметров)          |
| Категория → Товары       | Многие-ко-многим | ❌ (категория сохраняется)        |

---

### ⚠️ Особенности
1. **При удалении товара**:
   - Автоматически удаляются все его зависимые сущности (изображения, цвета, параметры)
   - Категории/теги/метки остаются в системе
   - Связи в ассоциативных таблицах удаляются

2. **Уникальные ограничения**:
   ```python
   # Теги
   name = Column(String(100), unique=True)  # "новинка", "акция"
   
   # Категории
   name = Column(String(100), unique=True)  # "Электроника", "Одежда"
   ```

---

### 🛠️ Основные функции  
#### 1. Периодическая загрузка данных  
- **Источники**:  
  ```python  
  API_URLS = [  
      "https://bot-igor.ru/api/products?on_main=true",  
      "https://bot-igor.ru/api/products?on_main=false"  
  ]  
  ```  
- **Задача Celery**: Автоматическое обновление каждые `CELERY_BEAT_SCHEDULE` секунд.  
- **Логирование**: Все операции фиксируются в `logs/app.log`.  

#### 2. Маршрут `/info`  
Возвращает сводку данных в произвольном формате

**Фильтрация и пагинация**:  
- `http://localhost:5555/info?category=Техника`
- `http://localhost:5555/info?category=Техника&category=Учебники`
- `http://localhost:5555/info?tags=1`
- `http://localhost:5555/info?tags=2&tags=5`
- `http://localhost:5555/info?page=1&count=200`

---

### 📄 Инструкция по эксплуатации  
#### Запуск вручную:  
```bash  
# Инициализация БД  
alembic upgrade head  

# Запуск Flask  
gunicorn -w 4 -b 0.0.0.0:5555 app:app  

# Запуск Celery  
celery -A tasks.celery worker --loglevel=info --beat  
```  
### 💾 Данные для проверки  
1. **После запуска**:  
   - Автоматическое создание таблиц (Alembic миграции).  
   - Заполнение БД данными из API(Celery + Celery Beat).  
2. **Логи**:  
   Используется библиотека loguru, в которой настроена для записи в файл логов

---

> Проект завершен. Готов к проверке! ✅