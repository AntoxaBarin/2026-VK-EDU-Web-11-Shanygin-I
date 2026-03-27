# StackUnderflow

## To view website

1. Run the server:

Native run:
```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python manage.py runserver
# Open http://localhost:8080
```

Using Docker Compose:
```bash
docker-compose up --build
```

## Routes

- `/ (index.html)`
- `/ask`
- `/profile`
- `/question`
- `/tag`
- `/hot`
- `/signup`
- `/login`
