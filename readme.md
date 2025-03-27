
# HBP Web App

A web application for checking for periods of time during which oil
wells or gas wells ceased producing, to help determine whether an oil
and gas lease remains "Held By Production" (an industry term usually
abbreviated as "HBP").


## Why?

An "oil and gas lease" is a high-value contract between a landowner and
an oil  company that lays out the terms for the company to drill wells
on the land. A typical lease will be maintained indefinitely, for 
however long oil or gas is being consistently produced -- hence "held 
(active) by production".

A typical lease allows gaps in production of only 60 or 90 consecutive 
days before automatically terminating. And because termination is 
(legally and contractually) automatic, it might not be noticed right 
away, which can open up the company to costly litigation or loss of the 
asset altogether. That might be avoided if they discover the issue early
enough to negotiate a more favorable resolution.


# To deploy locally...

### Option 1 - Docker

1) `git clone <this repo>`
2) `docker-compose up --build`

This option does not require installing MongoDB locally or setting up a 
cloud instance, but it becomes tricky to have the database persist if 
the Docker image needs to be rebuilt. That said, the database is only 
used to cache free public records anyway, so that might not be an 
issue.

### Option 2

If you want more control over the database (e.g., if you want to use a 
cloud instance of MongoDB; or if you want easier persistence), you might
want to go this route:

1) `git clone <this repo>`
2) `pip install -r requirements.txt`
3) Locally install [MongoDB](https://www.mongodb.com/try/download/community)
or set up a cloud instance. \*\*
4) Copy `.env.example` to `.env` and configure however you want. \*\*
5) Run `app.py`

\*\* The default `.env.example` is configured for a very basic, 
unsecured local database. In production, we would want to change `.env`
to configure MongoDB Cloud, etc.


# Usage Guide and API Endpoints

The production gaps for a collection of wells can be obtained as either
a text-based report or in JSON format.

*(Note that "API number" refers to a unique well ID that adheres to the 
__American Petroleum Institute__'s format. It's unfortunate but 
unavoidable that the same acronym has two meanings here.)*

### Get a text report of all production gaps

The main page will generate a 
[static HTML report](https://htmlpreview.github.io/?https://github.com/JamesPImes/hbp_webapp/blob/master/_example_resources/sample_report.htm) 
for the requested wells, showing the gaps in production (one version 
where wells in "shut-in" status are considered to be producing even when
they are not, and another version where the status of wells does not 
matter).

This report can be obtained in either of two ways:

* __Option #1__ - Enter well numbers in the web app

![](_example_resources/web_app_input.png)

* __Option #2__ - Use the `/well_group_report?api_nums=<...>` 
endpoint

Well numbers are separated by comma, as in the following example (in a
local deployment):

```
http://127.0.0.1:5000/well_group_report?api_nums=05-123-22710,05-123-21080,05-123-14244
```

### Get production gaps and well data as JSON

To get the same information (plus some additional detail) 
[in JSON format](_example_resources/sample_json.json),
use the `/well_group/` endpoint, separating well numbers by comma:

```
http://127.0.0.1:5000/well_group/05-123-22710,05-123-21080,05-123-14244
```
