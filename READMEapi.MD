
## 📘 Accounts API

Данный раздел API предоставляет CRUD-интерфейс для управления данными Telegram-аккаунтами в БД.


---

### 📌 Эндпоинты

#### 🔹 Создание аккаунта
**POST** `/accounts/`  
Создаёт новый аккаунт.
```json
{
  "is_authorized": true,
  "name": "string",
  "last_name": "string",
  "phone_number": "string",
  "api_id": 0,
  "api_hash": "string",
  "proxy_id": 0
}
```
**Request Body**: `AccountCreate`
**Response**: `AccountRead`

#### 🔹 Получение всех аккаунтов
**GET** `/accounts/`  
Возвращает список всех аккаунтов.

**Response**: `List[AccountRead]`

#### 🔹 Получение аккаунта по ID
**GET** `/accounts/{account_id}`  
Возвращает информацию об аккаунте по его ID.
```json
{
  "is_authorized": true,
  "name": "string",
  "last_name": "string",
  "phone_number": "string",
  "api_id": 0,
  "api_hash": "string",
  "proxy_id": 0,
  "id": 0
}
```
**Path Param**: `account_id` — `int`
**Response**: `AccountRead`
**404**: Если аккаунт не найден

#### 🔹 Обновление аккаунта
**PUT** `/accounts/{account_id}`  
Обновляет данные аккаунта по ID.

```json
{
  "is_authorized": true,
  "name": "string",
  "last_name": "string",
  "phone_number": "string",
  "api_id": 0,
  "api_hash": "string",
  "proxy_id": 0
}
```
**Path Param**: `account_id` — `int`

**Request Body**: `AccountUpdate`

**Response**: `AccountRead`

**404**: Если аккаунт не найден

#### 🔹 Удаление аккаунта
**DELETE** `/accounts/{account_id}`  
Удаляет аккаунт по ID.

**Path Param**: `account_id` — `int`

**Response**: `{ "detail": "Аккаунт успешно удален" }`

**404**: Если аккаунт не найден


---

## 🔐 Auth API

Этот модуль отвечает за авторизацию Telegram-аккаунтов через Telegram API с использованием кода подтверждения и возможной 2FA.

---

### 📌 Эндпоинты

#### 🔹 Отправка кода авторизации
**POST** `/auth/send-code`  
Отправляет код подтверждения на указанный номер телефона через Telegram API.

**Request Body**: `SendCodeRequest`
```json
{
  "phone_number": "+79998887766",
  "api_id": 12345,
  "api_hash": "your_api_hash",
  "proxy_id": 1
}
```
  
**Response**:
```json
  {
     "status": "ok",
     "message": "Code sent"
  }
```
 Вход с кодом (и опционально паролем 2FA)

**POST** `/auth/sign-in`
Завершает авторизацию, используя ранее отправленный код и, при необходимости, пароль 2FA.

**Request Body**: `SignInRequest`
```json
{
  "phone_number": "+79998887766",
  "code": "12345",
  "password": "optional_password",
  "api_id": 12345,
  "api_hash": "your_api_hash",
  "proxy_id": 1
}
```

## 📺 Channels API

Этот модуль предназначен для управления каналами, с которыми взаимодействуют аккаунты. Поддерживаются создание, просмотр и удаление каналов.

---

### 📌 Эндпоинты

#### 🔹 Создать канал
**POST** `/channels/create`  
Создаёт новый канал в базе данных.

**Request Body**: `ChannelCreate`

```json
{
  "name": "@Crypto_Signals",
  "comment": "Канал по криптовалюте",
  "status": "open"
}
```
**Response: ChannelResponse**

```json
{
  "id": 1,
  "name": "@Crypto_Signals",
  "comment": "Канал по криптовалюте",
  "status": "open",
  "request_count": 0,
  "accepted_request_count": 0
}
``` 
**GET** `/channels/get`
Возвращает список всех каналов.

**Response: List[ChannelResponse]**
```json
[
  {
    "id": 1,
    "name": "@Crypto_Signals",
    "comment": "Канал по криптовалюте",
    "status": "open",
    "request_count": 0,
    "accepted_request_count": 0
  }
]
```
**DELETE** `/channels/delete/{channel_id}`
    
Удаляет канал по ID.
	
**Response: ChannelResponse**
```json
{
  "id": 1,
  "name": "@Crypto_Signals",
  "comment": "Канал по криптовалюте",
  "status": "open",
  "request_count": 0,
  "accepted_request_count": 0
}
```
## 💬 Commenting API

Управление действиями ботов для комментирования постов в Telegram-каналах. Поддержка тональности комментариев, кастомных промптов и временной рандомизации.

---

### 📌 Эндпоинты

#### 🔹 Создать действие  
**POST** `/commenting/`  
Создаёт действие по комментированию.

**Request Body**: `CommentActionCreate`
```json
{
  "channel_id": 1,
  "positive_count": 2,
  "neutral_count": 1,
  "critical_count": 1,
  "question_count": 1,
  "custom_prompt": "Оставь комментарий про пользу домашних кошек",
  "action_time": 1800,
  "random_percentage": 20
}
 ```
**Response: CommentActionResponse**
```json
{
  "id": 3,
  "channel_id": 1,
  "positive_count": 2,
  "neutral_count": 1,
  "critical_count": 1,
  "question_count": 1,
  "custom_prompt": "Оставь комментарий про пользу канала",
  "action_time": 1800,
  "random_percentage": 20
}
```

#### 🔹 Получить все действия

**GET** `/commenting/`
	
    Response: List[CommentActionResponse]

⸻

#### 🔹 Получить действие по ID

**GET** `/commenting/{action_id}`
	
    Response: CommentActionResponse
    404 Not Found: Действие не найдено

⸻

#### 🔹 Обновить действие

**PUT** `/commenting/{action_id}`
	
    Request Body: CommentActionCreate
    Response: CommentActionResponse
    404 Not Found: Действие не найдено

⸻

#### 🔹 Удалить действие

**DELETE** `/commenting/{action_id}`
	
    Response: CommentActionResponse
    404 Not Found: Действие не найдено

⸻

#### 🔹 Выполнить действие

**POST** `/commenting/execute-action`
	
    Query Params:
    action_id: int
    api_id: str
    api_hash: str
	
**Response**:
```json
{
  "message": "Comment action executed successfully"
}
```

## 🌐 Proxy API

Управление прокси для аккаунтов Telegram. Возможность добавления, удаления и просмотра списка.

---

### 📌 Эндпоинты

#### 🔹 Добавить или обновить прокси  
**POST** `/proxy/add`

**Request Body**: `AddProxyRequest`
```json
{
    "ip_address": "192.168.0.1",
    "port": 8080,
    "login": "user1",
    "password": "pass123"
}
 ```
**Response**:
```json
{
  "message": "Proxy added or updated successfully"
}
```

#### 🔹 Удалить прокси по IP

**DELETE** `/proxy/delete?ip_address=192.168.0.1`

	Query Parameter:
	ip_address: str — IP адрес прокси


**Response (успех)**:
```json
{
  "status": "deleted",
  "ip": "192.168.0.1"
}
   ```
**404 Not Found**:
```json
{
  "detail": "Proxy not found"
}
```

#### 🔹 Получить список всех прокси

**GET** `/proxy/list`

**Response**:

```json
[
  {
    "id": 1,
    "ip_address": "192.168.0.1",
    "port": 8080,
    "login": "user1",
    "password": "pass123"
  },
  {
    "id": 2,
    "ip_address": "192.168.0.2",
    "port": 9090,
    "login": "user2",
    "password": "pass456"
  }
]
```

## ❤️ Reaction API

Автоматизация реакции на посты в Telegram-каналах с помощью эмодзи от заданного количества сессий.

---

### 📌 Эндпоинты

#### 🔹 Выполнить реакцию на последние посты  
**POST** `/reactions/execute-action`

**Query Parameter**:

  `action_id: int` — ID действия с реакцией

**Response**:
```json
{
  "message": "Reaction action executed successfully"
}
 ```
**404 Not Found:**
```json
{
  "detail": "Reaction action not found"
}
 ```
  
#### 🔹 Создать действие реакции

**POST /reactions/**

**Request Body: ReactionActionCreate**

  ```json
  {
  "channel_id": 12345,
  "emoji": "👍",
  "count": 10,
  "action_time": 600,
  "random_percentage": 20
  }
  ```
**Response: ReactionActionResponse**
  ```json
  {
  "id": 1,
  "channel_id": 12345,
  "emoji": "👍",
  "count": 10,
  "action_time": 600,
  "random_percentage": 20
  }
  ```
#### 🔹 Получить все действия

**GET** `/reactions/`
	
  `Response: List[ReactionActionResponse]`

⸻

#### 🔹 Получить действие по ID

**GET** `/reactions/{action_id}`

	Response: ReactionActionResponse

**404 Not Found**:
```json
  {
    "detail": "Reaction action not found"
  }
```

#### 🔹 Обновить действие

**PUT** `/reactions/{action_id}`
	
     Request Body: ReactionActionCreate
     Response: ReactionActionResponse

⸻

#### 🔹 Удалить действие

**DELETE** `/reactions/{action_id}`

	Response: ReactionActionResponse

**404 Not Found**:
```json
{
  "detail": "Reaction action not found"
}
```

## 👁️ Views API

Добавление просмотров к постам Telegram-каналов с использованием сессий.

---

### 📌 Эндпоинты

#### 🔹 Выполнить добавление просмотров  
**POST** `/views/execute-action`

- **Query Parameter**:
  
- `action_id: int` — ID действия


**Response**:
```json
{
"message": "View action executed successfully"
}
```
**404 Not Found**:

```json
{
"detail": "View action not found"
}
```

🔹 Создать действие просмотра

**POST** `/views/`

	Request Body: ViewActionCreate

```json
{
  "channel_id": 12345,
  "count": 20,
  "action_time": 300,
  "random_percentage": 15
}
```
- Response: ViewActionResponse
```json
{
  "id": 1,
  "channel_id": 12345,
  "count": 20,
  "action_time": 300,
  "random_percentage": 15
}
```

#### 🔹 Получить все действия

**GET** `/views/`
	
    Response: List[ViewActionResponse]

⸻

#### 🔹 Получить действие по ID

**GET** `/views/{action_id}`
	
    Response: ViewActionResponse
	404 Not Found:
```json
{
  "detail": "View action not found"
}
```

#### 🔹 Обновить действие

**PUT** `/views/{action_id}`

	Request Body: ViewActionCreate
	Response: ViewActionResponse

⸻

#### 🔹 Удалить действие

**DELETE** `/views/{action_id}`

	Response: ViewActionResponse
	404 Not Found:

```json
{
  "detail": "View action not found"
}
```
