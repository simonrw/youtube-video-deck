# Youtube video deck

This program runs a web server that manages youtube subscriptions.

The main use case is to replace the now inactive [youtube-video-deck](https://youtube.videodeck.net/), which keeps track of individual subscriptions, and which videos have been watched already. This is a simple extension on top of Youtube itself, which does not split subscriptions down by channel/playlist. I personally find it hard to keep track of new videos when they are all in a single list. In addition, I do not regularly prune my subscriptions. This app allows a separate selection of channels/playlists than youtube itself, and therefore can be considered more for favourite entries.

It is implemented as a `Django` web application that allows the user to subscribe to multiple video sources (channels or playlists) and fetch any new videos when they are made available.

## Getting started

In order to get started with the code, get a [Youtube API key][youtube-api-key]. Then:

* Clone the code: `git clone https://github.com/mindriot101/youtube-video-deck.git`
* Change into the code directory: `cd youtube-video-deck`
* Create a `.env` file which lists all secrets used, particularly the database connections, app secret key and google api key. A sample can be found under `env.sample`
* Install package dependencies with `pip`: `pip install -r requirements.txt`
* Install the node dependencies with `npm install`
* Compile the javascript/css code: `npm run prodbuild`
* Migrate your postgres database: `python ./manage.py migrate`
* Create the superuser, who has admin priviliges: `python ./manage.py createsuperuser`
* Start the app: `python ./manage.py runserver`

Alternatively the repository includes a `docker-compose.yml` file for use with `docker compose`. This reads secrets from the `.env` file, and spins up the web app and postgres database. Before the app will work, the same database migrations and superuser creation must occur, so the recommended approach is:

```
docker-compose up -d db
docker-compose up -d ytvd
docker-compose exec ytvd bash

# Within container
python ./manage.py migrate
python ./manage.py createsuperuser
exit

# Now back in the host shell
docker-compose restart ytvd
```

## Design

See the [design docs](./design/design.md)

## Alternatives

youtube-video-deck: this seems to have been discontinued. We are basically re-implementing this but simplifying the authentication

freetube: this can list subscriptions, but does not remove items that have been viewed

[youtube-api-key]: https://console.cloud.google.com/apis/credentials