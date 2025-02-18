FROM python:3

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --root-user-action=ignore


EXPOSE 8000

ENV SECRET_KEY=django-insecure-jd^afwkewci$y50d5a332nmv(y!zs5l%5ru6yui4h-4o5%5)he
ENV DEBUG=1
ENV DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]