# One Job management:

## Create new job

```bash
curl -X 'POST' \
  'http://127.0.0.1:5000/api/1/tasks/' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: 4fe2b4e9b0414f82bd2a5a6527c5e2e8' \
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
  'http://127.0.0.1:5000/api/1/tasks/12' \
  -H 'accept: application/json'
```

# Jobs collection

```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/tasks/' \
  -H 'accept: application/json'
```