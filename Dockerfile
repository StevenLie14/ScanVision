FROM python:3.12.4-slim-bullseye
RUN apt-get update --allow-unauthenticated && apt-get install ffmpeg libsm6 libxext6  -y
WORKDIR /app
COPY ./requirements.txt .
RUN pip install --upgrade pip --quiet && \
    pip install --quiet -r requirements.txt
ENV MPLBACKEND=Agg
COPY . .
EXPOSE 5500
ENTRYPOINT ["python", "server/main.py"]

