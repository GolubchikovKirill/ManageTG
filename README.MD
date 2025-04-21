# API Documentation

## Authentication Endpoints

### `POST /auth/send-code`

Отправка кода для авторизации через Telegram.

#### Request

```json
{
  "phone_number": "string",
  "api_id": 123456,
  "api_hash": "string",
  "proxy_id": 1
}
```

```json
{
  "status": "ok",
  "message": "Code sent successfully"
}

```


### `POST /auth/sign-in`

Авторизация в Telegram с использованием кода.
```json
{
  "phone_number": "string",
  "api_id": 123456,
  "api_hash": "string",
  "proxy_id": 1,
  "code": "string",
  "phone_code_hash": "string",
  "password": "string (optional)"
}
```
```json
{
  "status": "ok",
  "message": "Successfully signed in"
}
```

Если требуется двухфакторная аутентификация:
```json
{
  "status": "2fa_required",
  "message": "2FA password required"
}
```
## Action Endpoints

### `POST /actions/`

Создание нового действия для бота.
```json
{
  "channel_id": 1,
  "action_type": "comment",
  "count": 10,
  "action_time": 5,
  "random_percentage": 30
}
```
```json
{
  "id": 1,
  "channel_id": 1,
  "action_type": "comment",
  "count": 10,
  "action_time": 5,
  "random_percentage": 30
}
```

### `GET /actions/`

Получение списка всех действий.
```json
[
  {
    "id": 1,
    "channel_id": 1,
    "action_type": "comment",
    "count": 10,
    "action_time": 5,
    "random_percentage": 30
  },
  {
    "id": 2,
    "channel_id": 2,
    "action_type": "reaction",
    "count": 5,
    "action_time": 3,
    "random_percentage": 10
  }
]
```

### `DELETE /actions/{action_id}`

Удаление действия по ID.
```json
{
  "id": 1,
  "channel_id": 1,
  "action_type": "comment",
  "count": 10,
  "action_time": 5,
  "random_percentage": 30
}
```

### `PUT /actions/{action_id}`

Обновление действия.
```json
{
  "channel_id": 1,
  "action_type": "reaction",
  "count": 15,
  "action_time": 3,
  "random_percentage": 50
}
```
```json
{
  "id": 1,
  "channel_id": 1,
  "action_type": "reaction",
  "count": 15,
  "action_time": 3,
  "random_percentage": 50
}
```

## Channel Endpoints

### `POST /channels/create`

Создание нового канала.
```json
{
  "name": "Test Channel",
  "comment": "This is a test channel",
  "status": "open"
}
```
```json
{
  "id": 1,
  "name": "Test Channel",
  "comment": "This is a test channel",
  "status": "open",
  "request_count": 0,
  "accepted_request_count": 0
}
```

### GET /channels/get`

Получение списка всех каналов.
```json
[
  {
    "id": 1,
    "name": "Test Channel",
    "comment": "This is a test channel",
    "status": "open",
    "request_count": 0,
    "accepted_request_count": 0
  },
  {
    "id": 2,
    "name": "Sample Channel",
    "comment": "Sample channel description",
    "status": "private",
    "request_count": 5,
    "accepted_request_count": 3
  }
]
```

### `DELETE /channels/delete/{channel_id}`

Удаление канала по ID.
```json
{
  "id": 1,
  "name": "Test Channel",
  "comment": "This is a test channel",
  "status": "open",
  "request_count": 0,
  "accepted_request_count": 0
}
```

## Proxy Endpoints

### `POST /proxy/add`

Добавление нового прокси.
```json
{
  "ip_address": "192.168.1.1",
  "login": "user",
  "password": "password",
  "port": 8080
}
```
```json
{
  "message": "Proxy added or updated successfully"
}
```

### `DELETE /proxy/delete`

Удаление прокси по IP адресу.
```json
{
  "ip_address": "192.168.1.1"
}
```
```json
{
  "status": "deleted",
  "ip": "192.168.1.1"
}
```

### `GET /proxy/list`

Получение списка всех прокси.
```json
[
  {
    "id": 1,
    "ip_address": "192.168.1.1",
    "port": 8080,
    "login": "user",
    "password": "password"
  },
  {
    "id": 2,
    "ip_address": "192.168.1.2",
    "port": 8081,
    "login": "admin",
    "password": "admin"
  }
]
```

## Commenting Endpoints

### `POST /commenting/execute-action`

Запуск действия для всех сессий (комментарий, реакция, просмотр).
```json
{
  "action_id": 1,
  "api_id": "your_api_id",
  "api_hash": "your_api_hash"
}
```
```json
{
  "message": "Action executed successfully"
}
```


