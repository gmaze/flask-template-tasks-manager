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
  -H 'X-API-KEY: 8f0f6b0698e545c0a0c70a0aa6e99e5e' \
  -H 'accept: application/json'
```

# Get one user data
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/users/' \
  -H 'X-API-KEY: e353e0ad1de149bcb26f41e2b0a35e75' \
  -H 'accept: application/json'
```