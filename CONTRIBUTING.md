# Contributing

Thank you for your interest in developing `ytvd` further. I really appreciate your input, in whatever way!

Assistance is definitely welcomed in the following areas:

* **testing** - the code base has tests for the models and business logic, but at the moment no tests for presentation or views
* **documentation** - internal documentation for the methods, classes and functions is sparse at the moment, so any input would be appreciated
* **modernisation** - the code base is currently implemented via entirely server-side rendering, which adds UX problems e.g. when fetching many updates from the API
* **performance** - my understanding of Django is relatively little, so improving query efficiency would be greatly welcomed
* **UX design** - the current version can be considered "programmer art" throughout

## Development

### Backend

Follow the instructions in the README about fetching the code up to the "start the app" phase. By this point you should have the core app, but without some testing dependencies.

* Install testing dependencies: `pip install pytest pytest-django`
* Run the tests: `pytest`

The tests can be filtered to:

* Exclude tests that touch the database: `pytest -m "not django_db"`
* Exclude tests that make external HTTP calls: `pytest -m "not webtest"` (note these tests do not hit the Youtube API so an API key is not required)

### Frontend

There is no javascript at the moment, but the frontend uses `tailwindcss` for styling and layout. This is compiled into a single javascript bundle via `webpack`.

An initial graphql API was implemented via `graphene` but this is currently disabled.