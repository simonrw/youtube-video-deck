# Youtube video deck

This program runs a web server that manages youtube subscriptions.

The main use case is to replace youtube-video-deck, which keeps track of individual subscriptions, and which videos have been watched already.

## Design

See the [design docs](./design/design.md)

## Alternatives

youtube-video-deck: this seems to have been discontinued. We are basically re-implementing this but simplifying the authentication

freetube: this can list subscriptions, but does not remove items that have been viewed
