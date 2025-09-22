FROM python:3.11-slim

ARG PORT=8000
ENV PORT=${PORT}

WORKDIR /app

RUN mkdir -p web \
  && printf '<!doctype html>\n<html lang="pt-BR">\n<head>\n  <meta charset="utf-8" />\n  <title>Tabula</title>\n</head>\n<body>\n  <!-- Conteúdo publicado via rsync -->\n</body>\n</html>\n' > web/index.html

EXPOSE ${PORT}
CMD ["sh", "-c", "python -m http.server ${PORT:-8000} --directory web"]
