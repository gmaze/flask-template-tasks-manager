# One Job management:

## Create new job

```bash
curl -X 'POST' \
  'http://127.0.0.1:5000/api/1/tasks/' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: 4e0a718d648844a3a7f8cebc6c06ea61' \
  -H 'Content-Type: application/json' \
  -d '{
  "nfloats": 100,
  "label": ""
}'
```

## Get job info:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/tasks/12' \
  -H 'accept: application/json'
```

## Cancel running job:
```bash
curl -X 'DELETE' \
  'http://127.0.0.1:5000/api/1/tasks/23' \
  -H 'X-API-KEY: 4fe2b4e9b0414f82bd2a5a6527c5e2e8' \
  -H 'accept: application/json'
```

# Tasks

## GET

### For a user to get all its tasks:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/tasks/' \
  -H 'X-API-KEY: b09387d5d8d447268d88f8e09e54373f' \
  -H 'accept: application/json'
```

### For a user to get one task:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/tasks/7' \
  -H 'X-API-KEY: b09387d5d8d447268d88f8e09e54373f' \
  -H 'accept: application/json'
```

### For a user to get someone else task (error):
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/tasks/2' \
  -H 'X-API-KEY: b09387d5d8d447268d88f8e09e54373f' \
  -H 'accept: application/json'
```

### For an admin to get someone else task:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/tasks/2' \
  -H 'X-API-KEY: e128584706e24065995c0b99b042a945' \
  -H 'accept: application/json'
```

### For an admin to get all tasks:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/tasks/all' \
  -H 'X-API-KEY: e128584706e24065995c0b99b042a945' \
  -H 'accept: application/json'
```

### For any user to get all tasks (error):
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/tasks/all' \
  -H 'X-API-KEY: 25fce900e1d64052b9713601335f9a5b' \
  -H 'accept: application/json'
```

## POST

### For a user to submit a new task:

```bash
curl -v -X POST \
  'http://127.0.0.1:5000/api/1/tasks/' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: 25fce900e1d64052b9713601335f9a5b' \
  -H 'Content-Type: application/json' \
  -d '{
  "nfloats": 1000,
  "label": "dummy run"
}'
```


# Users

## GET

### For a user to get its data:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/users/' \
  -H 'X-API-KEY: b09387d5d8d447268d88f8e09e54373g' \
  -H 'accept: application/json'
```

### From admin to get all users data:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/users/all' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: e128584706e24065995c0b99b042a945'
```

From any user:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/users/all' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: 25fce900e1d64052b9713601335f9a5b'
```

### From admin to get one user data:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/users/3' \
  -H 'X-API-KEY: e128584706e24065995c0b99b042a945' \
  -H 'accept: application/json'
```

From any user (error):
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/users/2' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: 25fce900e1d64052b9713601335f9a5b'
```

## PUT

### From a user to update its profile:

```bash
curl -X 'PUT' \
  'http://127.0.0.1:5000/api/1/users/' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: b09387d5d8d447268d88f8e09e54373g' \
  -H 'Content-Type: application/json' \
  -d '{
  "plan_id": 3
}'
```