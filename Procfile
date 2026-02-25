# Heroku Procfile
web: cd quant/backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
release: cd quant/backend && alembic upgrade head
