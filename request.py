#!/usr/bin/env python


import requests
import os
import dotenv
import psycopg2
from psycopg2.errors import UniqueViolation
import logging
from contextlib import contextmanager


username = "outsidexbox"


class Database:

    TABLENAME = "ytvd"

    def __init__(self, filename, connection_options):
        self._filename = filename
        self._conn = psycopg2.connect(
            user=connection_options["username"],
            database=connection_options["database"],
            host=connection_options.get("hostname", "localhost"),
            password=connection_options["password"],
        )
        self._logger = logging.getLogger("scraper.db")

    def drop(self):
        with self._conn as conn:
            cursor = conn.cursor()
            self._execute(cursor, """DROP TABLE IF EXISTS {}""".format(self.TABLENAME))

    def create(self):
        with self._conn as conn:
            cursor = conn.cursor()
            self._execute(
                cursor,
                """CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    video_id TEXT NOT NULL,
                    watched BOOLEAN NOT NULL DEFAULT FALSE,
                    UNIQUE(video_id)
                    )""".format(
                    self.TABLENAME
                ),
            )

    def save(self, cursor, entry):
        self._execute(
            cursor,
            """INSERT INTO {} (video_id) values (%s)""".format(self.TABLENAME),
            (entry["id"],),
        )

    @contextmanager
    def tx(self):
        with self._conn as conn:
            cursor = conn.cursor()
            yield cursor

    def _execute(self, cursor, query, args=None):
        self._logger.debug(cursor.mogrify(query, args).decode())
        return cursor.execute(query, args)


class Client:
    def __init__(self, key, database):
        self.key = key

    def _fetch_channel_info(self, username):
        url = "https://www.googleapis.com/youtube/v3/channels?part={part}&key={key}&forUsername={username}".format(
            part="contentDetails", key=self.key, username=username
        )
        r = requests.get(url)
        r.raise_for_status()
        results = r.json()
        return results["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def _fetch_items(self, uploads_id):
        page = None
        while True:
            url = "https://www.googleapis.com/youtube/v3/playlistItems?key={key}&part=contentDetails&maxResults=50&playlistId={playlist_id}".format(
                key=self.key, playlist_id=uploads_id
            )
            if page is not None:
                url += "&pageToken={page}".format(page=page)

            r = requests.get(url)
            r.raise_for_status()
            data = r.json()
            for every in data["items"]:
                published_at = every["contentDetails"]["videoPublishedAt"]
                id = every["id"]
                yield {"date": published_at, "id": id}

            page = data.get("nextPageToken", None)
            if not page:
                break

    def upload_for(self, username):
        uploads_id = self._fetch_channel_info(username)
        for video in self._fetch_items(uploads_id):
            yield video


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # Disable other loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger = logging.getLogger("scraper.main")

    dotenv.load_dotenv()

    db = Database(
        "db.db",
        connection_options=dict(
            username=os.environ["DATABASE_USERNAME"],
            database=os.environ["DATABASE_DBNAME"],
            hostname=os.environ.get("DATABASE_HOSTNAME", "localhost"),
            password=os.environ["DATABASE_PASSWORD"],
        ),
    )
    # db.drop()
    db.create()

    key = os.environ["GOOGLE_API_KEY"]

    client = Client(key, db)

    for item in client.upload_for(username):
        with db.tx() as cursor:
            try:
                db.save(cursor, item)
            except UniqueViolation:
                logger.info("object %s exists in database, skipping", item)
                continue
            except Exception as e:
                raise e
