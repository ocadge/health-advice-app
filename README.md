# Environmental Health Advice App

A desktop app that helps people, especially those with heart or lung conditions, decide whether it's safe to spend time outside. It shows the weather and air quality for a location on an interactive map, with health advice based on the air quality level.

I built it for my T Level Digital Production, Design and Development employer-set project (2023).

## Features

- Finds your approximate location and shows it on an interactive map
- Live weather (OpenWeatherMap) and air quality (World Air Quality Index)
- Health advice by UK Daily Air Quality Index band (Low, Moderate, High, Very High), with separate advice for at-risk people
- Steps-to-calories health tracker
- Dark mode and map style settings
- Every request is logged to a local SQLite database

## Tech

Python, customtkinter, tkintermapview, requests, Pillow, SQLite

## Setup

1. `pip install customtkinter tkintermapview requests pillow`
2. Get your own free API keys:
   - OpenWeatherMap: https://openweathermap.org/api
   - WAQI air quality token: https://aqicn.org/data-platform/token/
3. Copy `.env.example` to `.env` and add your keys (or set the `OPENWEATHER_API_KEY` and `WAQI_API_TOKEN` environment variables).
4. Add three 24px icons to an `images/` folder next to the script: `settings_icon.png`, `tracker_icon.png` and `return_icon.png`. They aren't included in this repo because of their licence; any free icon set works.
5. Run `python HealthAdviceGroup.py`.

`.env` and the local database are git-ignored, so keys and logged requests are never uploaded.

## What I learned

- Calling REST APIs and handling JSON responses
- Building a desktop GUI with an interactive map
- Planning a project properly: requirements, flowcharts, a test strategy and a bug log
- Keeping secrets out of code. My first version had API keys written in the code; I refactored it to load them from a `.env` file.
