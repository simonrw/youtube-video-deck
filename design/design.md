---
title: Design document
---

# Design doc

## Objectives

The app should support the following functionalities (in order of imporatance):

1. Allow the user to check their subscriptions for the latest videos
2. Support channels and playlists
3. Search for channels or playlists
4. Do not require _youtube_ authentication for the user
3. *(optional)* Support authentication using multiple methods (oauth, username/pw)

## Components

### Domain models (mapping to database tables)

#### Subscription

*Responsibilities*

* links the subscription ID to a series of videos
* tracks the last time the subscription was checked for new items
* stores whether the subscription is a channel or playlist

![Subscription ERD](./subscription_erd.png)

#### Video

*Responsibilities*

* track whether the user has watched the video
* store the thumbnail
* store the full url to video

![Video ERD](./video_erd.png)

### Helper classes

#### Youtube client

This object decouples the domain models from the Youtube API. It supports the following methods:

* Search Youtube for either the channel or playlist with the given name
* Fetch new items (videos) since a specified time

#### Crawler

This concept performs the crawling of multiple subscriptions. This takes the Youtube Client class as a dependency and uses it to perform requests to the Youtube API. When given a user, it fetches the subscriptions from the user. For each subscription, it queries the Youtube API for new videos since the `Subscription`'s `last_fetched` date.

## Questions

* [x] can the API check multiple subscriptions (channels or playslists) in a single request? *no it cannot*
* [*] does the search method of the Youtube API return what the matched result
  is? *yes it does, and it can query for multiple types of result e.g. channels
  and playlists*
* [ ] django enumeration support (`Subscription.type` field)

## Initial sketch

The initial sketch drawn in a notebook is:

![Initial sketch of the implementation](./notebook_screenshot.jpg)
