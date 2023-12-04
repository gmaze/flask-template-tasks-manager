# One Job management:

## Create new job

```bash
curl -X 'POST' \
  'http://127.0.0.1:5000/api/1/tasks/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 12,
  "label": "",
  "nfloats": 12000
}'
```

## Get job info:
```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/tasks/36' \
  -H 'accept: application/json'
```

## Cancel running job:
```bash
curl -X 'DELETE' \
  'http://127.0.0.1:5000/api/1/tasks/58' \
  -H 'accept: application/json'
```

# Jobs collection

```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/api/1/tasks/' \
  -H 'accept: application/json'
```