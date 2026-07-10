# Ads API — Flask REST Service

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![Flask-SQLAlchemy](https://img.shields.io/badge/Flask_SQLAlchemy-3.0-2F7F9E?logo=sqlalchemy&logoColor=white)
![Flask-Login](https://img.shields.io/badge/Flask_Login-0.6-2F7F9E?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Werkzeug](https://img.shields.io/badge/Werkzeug-Security-1A1A1A)

REST API-сервис объявлений на **Flask** с системой прав и хешированием паролей. Поддерживает регистрацию, авторизацию и управление объявлениями с проверкой владельца.

Домашнее задание к лекции «Flask» (курс Python-разработчика, Нетология). Реализованы как основное (Задание 1), так и необязательное (Задание 2 — система прав) требования.

---

## Содержание

- [Возможности](#возможности)
- [Стек технологий](#стек-технологий)
- [Модель данных](#модель-данных)
- [API Endpoints](#api-endpoints)
- [Система прав](#система-прав)
- [Быстрый старт](#быстрый-старт)
- [Примеры запросов](#примеры-запросов)
- [Структура проекта](#структура-проекта)
- [Технические решения](#технические-решения)

---

## Возможности

### Задание 1 (базовое)

- POST `/ads` — создание объявления
- GET `/ads` — получение всех объявлений
- GET `/ads/<ad_id>` — получение конкретного объявления
- DELETE `/ads/<ad_id>` — удаление объявления

Поля объявления: `title`, `description`, `created_at`, `owner_id`.

### Задание 2 (необязательное — система прав)

- Регистрация пользователя с email и хешем пароля
- Авторизация через Flask-Login (session-based)
- Создание объявления доступно только авторизованным пользователям
- Удаление/редактирование объявления доступно только его владельцу
- Кастомные декораторы `@login_required` и `@owner_required`

---

## Стек технологий

| Компонент | Технология | Назначение |
|-----------|-----------|------------|
| Web-фреймворк | Flask 3.0 | REST API и маршрутизация |
| ORM | Flask-SQLAlchemy 3.0 | Работа с базой данных |
| Аутентификация | Flask-Login 0.6 | Session-based авторизация |
| Безопасность | Werkzeug Security | Хеширование паролей (pbkdf2) |
| База данных | SQLite | Хранение пользователей и объявлений |
| Структура | Application Factory | Паттерн `create_app()` |

---

## Модель данных

### User

| Поле | Тип | Описание |
|------|-----|---------|
| `id` | Integer (PK) | Идентификатор |
| `email` | String(100), unique | Email (логин) |
| `password_hash` | String(200) | Хеш пароля (werkzeug) |

Методы:
- `set_password(password)` — установка хеша пароля
- `check_password(password)` — проверка пароля

### Advertisement

| Поле | Тип | Описание |
|------|-----|---------|
| `id` | Integer (PK) | Идентификатор |
| `title` | String(100) | Заголовок |
| `description` | Text | Описание |
| `created_at` | DateTime | Дата создания (автогенерация, UTC) |
| `owner_id` | Integer (FK → user.id) | Владелец |

Связь с `User` через `relationship` (`owner`).

---

## API Endpoints

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| POST | `/register` | Регистрация пользователя | Открытый |
| POST | `/login` | Авторизация | Открытый |
| GET | `/ads` | Список всех объявлений | Открытый |
| GET | `/ads/<ad_id>` | Получение по ID | Открытый |
| POST | `/ads` | Создание объявления | Авторизованный |
| DELETE | `/ads/<ad_id>` | Удаление объявления | Владелец |

### Форматы запросов/ответов

**POST `/register`** — регистрация:
```json
// Запрос
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
// Ответ 201
{
  "message": "User created"
}
```

**POST `/login`** — авторизация:
```json
// Запрос
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
// Ответ 200
{
  "message": "Logged in"
}
```

**POST `/ads`** — создание объявления:
```json
// Запрос (с cookie авторизованного пользователя)
{
  "title": "iPhone 13 Pro",
  "description": "Отличное состояние"
}
// Ответ 201
{
  "id": 1,
  "title": "iPhone 13 Pro",
  "description": "Отличное состояние",
  "created_at": "2025-01-15T12:30:00",
  "owner_id": 1
}
```

**GET `/ads`** — список всех объявлений:
```json
[
  {
    "id": 1,
    "title": "iPhone 13 Pro",
    "description": "Отличное состояние",
    "created_at": "2025-01-15T12:30:00",
    "owner_id": 1
  }
]
```

---

## Система прав

### Иерархия доступа

| Действие | Неавторизованный | Авторизованный | Владелец объявления |
|----------|------------------|----------------|---------------------|
| Регистрация | ✅ | ✅ | ✅ |
| Авторизация | ✅ | ✅ | ✅ |
| Просмотр объявлений | ✅ | ✅ | ✅ |
| Создание объявления | ❌ (401) | ✅ | ✅ |
| Удаление своего объявления | ❌ | ❌ (403) | ✅ |
| Удаление чужого объявления | ❌ | ❌ (403) | ❌ (403) |

### Кастомные декораторы

Реализованы в `auth.py`:

```python
@login_required
def create_ad():
    """Доступен только авторизованным пользователям"""
    ...

@owner_required
def delete_ad(ad_id):
    """Доступен только владельцу объявления"""
    ...
```

- `@login_required` — проверяет `current_user.is_authenticated`, иначе возвращает **401**
- `@owner_required` — проверяет, что `ad.owner_id == current_user.id`, иначе возвращает **403**

---

## Быстрый старт

### Предварительные требования

- Python 3.9+

### Установка

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/YES-I-AM-EVIL/py-homeworks-web-2.1-flask.git
cd py-homeworks-web-2.1-flask

# 2. Создайте и активируйте виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .\.venv\Scripts\activate  # Windows

# 3. Установите зависимости
pip install flask flask-sqlalchemy flask-login werkzeug

# 4. Запустите приложение
python app.py
```

Сервис будет доступен на `http://127.0.0.1:5000/`.

База данных `ads.db` (SQLite) создаётся автоматически при первом запуске.

---

## Примеры запросов

### Регистрация

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'
```

### Авторизация (сохраняет session cookie)

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'
```

### Создание объявления (с cookie)

```bash
curl -X POST http://localhost:5000/ads \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "iPhone 13 Pro",
    "description": "Отличное состояние,全套 комплект"
  }'
```

### Получение всех объявлений

```bash
curl http://localhost:5000/ads
```

### Получение по ID

```bash
curl http://localhost:5000/ads/1
```

### Удаление (только владелец)

```bash
curl -X DELETE http://localhost:5000/ads/1 \
  -b cookies.txt
```

### Попытка удаления чужого объявления

```bash
# Возвращает 403 Forbidden
curl -X DELETE http://localhost:5000/ads/999 \
  -b cookies.txt
```

---

## Структура проекта

```
py-homeworks-web-2.1-flask/
├── app.py                       # Application Factory (create_app)
├── models.py                    # SQLAlchemy-модели: User, Advertisement
├── routes.py                    # Flask-роуты (init_routes)
├── auth.py                      # Декораторы login_required, owner_required
└── README.md                     # Документация проекта
```

---

## Технические решения

### 1. Application Factory Pattern

Используется паттерн `create_app()` для лучшей тестируемости и расширяемости:

```python
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ads.db'

    db.init_app(app)
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    init_routes(app)

    with app.app_context():
        db.create_all()

    return app
```

Преимущества:
- Возможность создавать несколько приложений с разной конфигурацией
- Изоляция состояния между тестами
- Чёткое разделение инициализации и роутинга

### 2. Безопасное хранение паролей

Используется `werkzeug.security` — промышленный стандарт хеширования с солью:

```python
class User(db.Model, UserMixin):
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

Пароли никогда не хранятся в открытом виде — только хеши через `pbkdf2:sha256`.

### 3. Session-based авторизация через Flask-Login

После успешного `/login` создаётся сессия, которая сохраняется в cookie. Flask-Login управляет состоянием `current_user` автоматически:

```python
@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not user.check_password(data.get('password')):
        return jsonify({"error": "Invalid credentials"}), 401
    login_user(user)
    return jsonify({"message": "Logged in"})
```

### 4. Кастомные декораторы для проверки прав

Декораторы `@login_required` и `@owner_required` инкапсулируют логику доступа и переиспользуются между роутами:

```python
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    @wraps(f)
    def decorated_function(ad_id, *args, **kwargs):
        ad = Advertisement.query.get_or_404(ad_id)
        if ad.owner_id != current_user.id:
            return jsonify({"error": "Forbidden: Not the owner"}), 403
        return f(ad_id, *args, **kwargs)
    return decorated_function
```

### 5. Сериализация через `to_dict()`

Модель `Advertisement` содержит метод `to_dict()` для удобной конвертации в JSON:

```python
class Advertisement(db.Model):
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "owner_id": self.owner_id
        }
```

### 6. Автогенерация даты создания

Поле `created_at` заполняется автоматически при создании записи:

```python
created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 7. Автоматическое создание таблиц

Таблицы БД создаются при первом запуске приложения, без необходимости вручную выполнять миграции:

```python
with app.app_context():
    db.create_all()
