FROM python:3.7

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
    postgresql-client \
    nodejs \
    npm \
  && rm -rf /var/lib/apt/lists/*

RUN npm install -g npm

WORKDIR /usr/src/app

COPY package.json .
COPY package-lock.json .
RUN npm install

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY manage.py .
COPY postcss.config.js .
COPY subscriptions subscriptions
COPY tailwind.config.js .
COPY webpack.config.js .
COPY ytvd ytvd
COPY assets assets

# Perform the build
RUN npm run prodbuild

EXPOSE 8000

CMD ["python", "./manage.py", "runserver", "--noreload", "0.0.0.0:8000"]
