FROM python:3-slim AS build-env
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

FROM gcr.io/distroless/python3-debian12:nonroot
COPY --from=build-env /app /app
COPY --from=build-env /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

WORKDIR /app
ENV PYTHONPATH=/usr/local/lib/python3.12/site-packages
CMD ["ecr.py"]
