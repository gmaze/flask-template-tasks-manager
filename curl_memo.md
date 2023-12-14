# One Job management:

## Create new job

```bash
curl -X 'POST' \
  'http://127.0.0.1:5000/api/1/tasks/' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: 102142ac191e477c96b1c9255ca5a127' \
  -H 'Content-Type: application/json' \
  -d '{
  "nfloats": 12000,
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

# Jobs collection

```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/tasks/' \
  -H 'X-API-KEY: 25fce900e1d64052b9713601335f9a5b' \
  -H 'accept: application/json'
```

# Users

## For a user to get its data:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/users/' \
  -H 'X-API-KEY: 25fce900e1d64052b9713601335f9a5b' \
  -H 'accept: application/json'
```

## From admin to get all users data:
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

## From admin to get one user data:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/users/2' \
  -H 'X-API-KEY: e128584706e24065995c0b99b042a945' \
  -H 'accept: application/json'
```

From any user:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/users/2' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: 25fce900e1d64052b9713601335f9a5b'
```