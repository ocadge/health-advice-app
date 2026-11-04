# Import modules
import customtkinter
from tkintermapview import TkinterMapView
import requests
from PIL import Image
import os
import sqlite3
import datetime
import gc

from config import OPENWEATHER_KEY, WAQI_KEY


# Declare class
class App(customtkinter.CTk):
    # Declare the app name and size
    APP_NAME = "Health App"
    WIDTH = 1200
    HEIGHT = 800
    # Initialize the object state

    def __init__(self, *args, **kwargs):
        # Inherit the class data
        super().__init__(*args, **kwargs)
        # Set title, geometry and minimum size
        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)
        # Declare variables used for dashboard/map
        self.advice_exists = False
        self.weather_exists = False
        self.marker_list = []
        # Declare variables used for settings
        self.new_mode = customtkinter.StringVar(value="Dark")
        self.map_value = customtkinter.StringVar(value="OpenStreetMap")
        # Declare variables used for health tracker
        self.MET = 2.8
        self.speed = 0.9

        # Enable garbage collection
        gc.enable()

        # Declare image path
        self.image_path = os.path.join(
            os.path.dirname(
                os.path.realpath(__file__)),
            "images")

        # Declaring API keys
        # OpenWeatherMap key (loaded from config.py / environment, never hard-coded) ~~ more info:
        # https://openweathermap.org/api
        self.weatherkey = OPENWEATHER_KEY
        # World Air Quality Index standard key ~~ more info:
        # https://aqicn.org/api/
        self.aqikey = WAQI_KEY
        # Set the default appearance to 'Dark'
        customtkinter.set_appearance_mode("Dark")
        # Bind closing commands to on_closing function
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)
        # Display the dashboard
        self.dashboard()

    def dashboard(self):
        # Reset default values
        self.advice_exists = False
        self.weather_exists = False
        self.marker_list = []
        # Get user location from user IP
        res = requests.get('https://ipinfo.io/')
        data = res.json()
        # Split data to get lat and lon
        user_coords = data['loc'].split(',')
        # Set lat and lon to user_coords and set the data type from string to
        # float
        lat = float(user_coords[0])
        lon = float(user_coords[1])

        # Create and configure CTk frames
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.frame_header = customtkinter.CTkFrame(
            master=self, corner_radius=15, fg_color=None)
        self.frame_header.grid(
            row=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="nesw")

        self.frame_map = customtkinter.CTkFrame(
            master=self, corner_radius=15, fg_color=None)
        self.frame_map.grid(
            row=1,
            rowspan=2,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="nesw")

        self.frame_setting = customtkinter.CTkFrame(
            master=self, corner_radius=15, fg_color=None)
        self.frame_setting.grid(row=3, column=0, padx=5, pady=5, sticky="nesw")

        self.frame_tracker = customtkinter.CTkFrame(
            master=self, corner_radius=15, fg_color=None)
        self.frame_tracker.grid(row=3, column=1, padx=5, pady=5, sticky="nesw")
        # Header Frame
        # Create widgets in the header frame
        self.overlay_option_menu = customtkinter.CTkOptionMenu(
            self.frame_header, values=[
                "Air Quality", "Temperature"], command=self.change_overlay)
        self.overlay_option_menu.grid(row=0, column=2, padx=5, pady=5)

        self.clear_button = customtkinter.CTkButton(
            master=self.frame_header,
            text="Clear Markers",
            width=160,
            command=lambda: self.clear_marker())
        self.clear_button.grid(row=0, column=3, sticky="nesw", padx=5, pady=5)

        self.search_entry = customtkinter.CTkEntry(
            master=self.frame_header, placeholder_text="Enter address", width=200)
        self.search_entry.grid(row=0, column=0, sticky="nesw", padx=5, pady=5)
        # Bind the return/enter key to search_event in the entry box
        self.search_entry.bind("<Return>", self.search_event)

        # Map Frame
        # Configure map frame
        self.frame_map.grid_columnconfigure(0, weight=1)
        self.frame_map.grid_rowconfigure(0, weight=1)
        self.frame_map.grid_rowconfigure(1, weight=1)
        # Create map widget
        self.map_widget = TkinterMapView(self.frame_map)
        self.map_widget.grid(
            row=0,
            rowspan=2,
            column=0,
            columnspan=3,
            sticky="nesw",
            padx=(
                0,
                0),
            pady=(
                0,
                0))
        # Set map starting position
        self.map_widget.set_position(lat, lon)
        # Add right click commands
        self.map_widget.add_right_click_menu_command(
            label="Get Current Air Quality",
            command=self.get_aqi_event,
            pass_coords=True)
        self.map_widget.add_right_click_menu_command(
            label="Get Current Weather",
            command=self.get_weather_event,
            pass_coords=True)
        # Initialize tile servers
        self.change_map(self.map_value.get())
        self.change_overlay("Air Quality")

        # Settings Button Frame
        # Configure settings frame
        self.frame_setting.grid_columnconfigure(0, weight=1)
        self.frame_setting.grid_rowconfigure(0, weight=1)
        # Create settings button
        self.setting_image = customtkinter.CTkImage(
            Image.open(
                os.path.join(
                    self.image_path, "settings_icon.png")), size=(
                100, 100))

        self.setting_button = customtkinter.CTkButton(
            master=self.frame_setting,
            text="Settings",
            width=360,
            height=120,
            font=(
                "Arial",
                30),
            corner_radius=15,
            image=self.setting_image,
            anchor="w",
            command=lambda: (
                self.destroy_children(),
                self.settings()))
        self.setting_button.grid(padx=10, pady=10, sticky="nesw")

        # Tracker Button Frame
        # Configure tracker frame
        self.frame_tracker.grid_columnconfigure(0, weight=1)
        self.frame_tracker.grid_rowconfigure(0, weight=1)
        # Create tracker button
        self.tracker_image = customtkinter.CTkImage(
            Image.open(
                os.path.join(
                    self.image_path, "tracker_icon.png")), size=(
                100, 100))

        self.tracker_button = customtkinter.CTkButton(
            master=self.frame_tracker,
            text="Health Tracker",
            width=200,
            height=120,
            font=(
                "Arial",
                30),
            corner_radius=15,
            image=self.tracker_image,
            anchor="w",
            command=lambda: (
                self.destroy_children(),
                self.health_tracker()))
        self.tracker_button.grid(padx=10, pady=10, sticky="nesw")

    def search_event(self, event=None):
        # Set the map address to the value inputted in the search_entry
        self.map_widget.set_address(self.search_entry.get())

    def clear_marker(self):
        # Delete all marker objects in marker_list
        for marker in self.marker_list:
            marker.delete()

    def change_map(self, new_map: str):
        # Set the map tile server to the value inputted
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server(
                "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google Maps":
            self.map_widget.set_tile_server(
                "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google Earth":
            self.map_widget.set_tile_server(
                "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Black & White":
            self.map_widget.set_tile_server(
                "http://a.tile.stamen.com/toner/{z}/{x}/{y}.png")

    def change_overlay(self, new_overlay: str):
        # Run the change_map function to reset the tiles when changing overlay
        self.change_map(self.map_value.get())
        # Set the overlay tile server to appropriate map overlay
        if new_overlay == "Air Quality":
            self.map_widget.set_overlay_tile_server(
                "https://tiles.aqicn.org/tiles/usepa-aqi/{z}/{x}/{y}.png?token=" + self.aqikey)
        elif new_overlay == "Temperature":
            self.map_widget.set_overlay_tile_server(
                "https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=" +
                self.weatherkey)

    def get_aqi_event(self, coords: str):
        # Set lat and lon according to the coords data inputted from the right
        # click menu
        print("Add marker: ", coords)
        lat = coords[0]
        lon = coords[1]
        res = requests.get(
            f"https://api.waqi.info/feed/geo:{lat};{lon}/?token=" +
            self.aqikey)
        data = res.json()
        # Set aqi to the json data pulled from the air quality api
        aqi = data['data']['aqi']
        # Set color and value of the text based on the aqi
        if aqi < 50:
            self.aqi_color = "#10911d"
            self.advice = "Air quality is considered satisfactory, and air pollution poses little or no risk"
        elif aqi < 100:
            self.aqi_color = "#b5a516"
            self.advice = "Air quality is acceptable; however, for some pollutants there\nmay be a moderate health concern for a very small number\nof people who are unusually sensitive to air pollution."
        elif aqi < 150:
            self.aqi_color = "#b56016"
            self.advice = "Members of sensitive groups may experience health effects.\nThe general public is not likely to be affected."
        elif aqi < 200:
            self.aqi_color = "#b81212"
            self.advice = "Everyone may begin to experience health effects; \nmembers of sensitive groups may experience more serious health effects"
        elif aqi < 300:
            self.aqi_color = "#5c0f94"
            self.advice = "Health warnings of emergency conditions. \nThe entire population is more likely to be affected."
        elif aqi > 300:
            self.aqi_color = "#450a0a"
            self.advice = "Health alert: everyone may experience more serious health effects"
        # Create marker on map widget and append it to marker list
        self.marker_list.append(
            self.map_widget.set_marker(
                coords[0],
                coords[1],
                text=aqi,
                text_color=self.aqi_color,
                font=(
                    "Helvetica",
                    15,
                    'bold'),
                marker_color_circle=self.aqi_color,
                marker_color_outside="black"))
        # Create advice widget
        self.show_advice()
        # Store request in the database
        self.aqi_db(lat, lon, aqi)

    def get_weather_event(self, coords: str):
        # Set lat and lon according to the coords data inputted from the right
        # click menu
        lat = coords[0]
        lon = coords[1]
        res = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=" +
            self.weatherkey +
            "&units=metric")
        data = res.json()
        # Set variables to the json data pulled from the temperature api
        self.temp = data['main']['temp']
        self.weather = data['weather'][0]['description']
        self.temp_min = data['main']['temp_min']
        self.temp_max = data['main']['temp_max']
        self.city = data['name']
        self.country = data['sys']['country']
        self.sunrise = data['sys']['sunrise']
        self.sunset = data['sys']['sunset']
        # Convert sunset and sunrise data from unix to readable time
        self.sunrisetext = datetime.datetime.fromtimestamp(self.sunrise)
        self.sunsettext = datetime.datetime.fromtimestamp(self.sunset)
        # Create weather widget
        self.show_weather()
        # Store request in database
        self.weather_db(lat, lon, self.temp, self.weather)

    def show_advice(self):
        # Create label with text according to the aqi
        # Check if label already exists, if it does destroy the existing label
        # and create a new one
        if self.advice_exists:
            self.destroy_advice()
            self.advice_label = customtkinter.CTkLabel(
                master=self.frame_map,
                text=self.advice,
                text_color=self.aqi_color,
                width=280,
                height=12,
                corner_radius=15)
            self.advice_label.grid(
                row=0, column=0, padx=5, pady=5, sticky="ne")
            self.closeaqi_button = customtkinter.CTkButton(
                master=self.advice_label, text="X", width=20, height=20, font=(
                    "Arial", 30), corner_radius=15, command=lambda: (
                    self.destroy_advice()))
            self.closeaqi_button.grid(
                row=0, column=1, padx=10, pady=10, sticky="ne")
            # Set exists to true
            self.advice_exists = True
        else:
            # If the label does not exist, create the label
            self.advice_label = customtkinter.CTkLabel(
                master=self.frame_map,
                text=self.advice,
                text_color=self.aqi_color,
                width=280,
                height=12,
                corner_radius=15)
            self.advice_label.grid(
                row=0, column=0, padx=5, pady=5, sticky="ne")
            self.closeaqi_button = customtkinter.CTkButton(
                master=self.advice_label, text="X", width=20, height=20, font=(
                    "Arial", 30), corner_radius=15, command=lambda: (
                    self.destroy_advice()))
            self.closeaqi_button.grid(
                row=0, column=1, padx=10, pady=10, sticky="ne")
            # Set exists to true
            self.advice_exists = True

    def show_weather(self):
        # Create frame with labels with text according to the temperature and weather data
        # Check if frame already exists, if it does destroy the existing frame
        # and create a new one
        if self.weather_exists:
            self.frame_weather.destroy()
            self.frame_weather = customtkinter.CTkFrame(
                master=self.frame_map, corner_radius=15, fg_color=None)
            self.frame_weather.grid(
                row=0, column=0, padx=5, pady=5, sticky="nw")
            self.temp_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=f"{self.temp}°C",
                text_color="#db2518",
                width=100,
                corner_radius=15,
                font=(
                    "Helvetica",
                    30))
            self.temp_label.grid(
                row=0, column=0, padx=5, pady=5, sticky="nesw")
            self.weather_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=self.weather.title(),
                text_color="#db2518",
                width=100,
                corner_radius=15,
                font=(
                    "Helvetica",
                    25))
            self.weather_label.grid(
                row=1, column=0, padx=5, pady=5, sticky="nesw")
            self.tempmin_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=f"min: {self.temp_min}°C",
                text_color="#9e2c2c",
                corner_radius=15,
                font=(
                    "Helvetica",
                    15))
            self.tempmin_label.grid(
                row=2, column=0, padx=5, pady=5, sticky="nesw")
            self.tempmax_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=f"min: {self.temp_max}°C",
                text_color="#9e2c2c",
                corner_radius=15,
                font=(
                    "Helvetica",
                    15))
            self.tempmax_label.grid(
                row=3, column=0, padx=5, pady=5, sticky="nesw")
            self.sunrise_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=f"Sunrise: {self.sunrisetext}",
                text_color="#9e2c2c",
                corner_radius=15,
                font=(
                    "Helvetica",
                    15))
            self.sunrise_label.grid(
                row=4, column=0, padx=5, pady=5, sticky="nesw")
            self.sunset_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=f"Sunset: {self.sunsettext}",
                text_color="#9e2c2c",
                corner_radius=15,
                font=(
                    "Helvetica",
                    15))
            self.sunset_label.grid(
                row=5, column=0, padx=5, pady=5, sticky="nesw")
            self.location_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=f"{self.city}, {self.country}",
                text_color="#9e2c2c",
                corner_radius=15,
                font=(
                    "Helvetica",
                    15))
            self.location_label.grid(
                row=6, column=0, padx=5, pady=5, sticky="nesw")
            self.closetemp_button = customtkinter.CTkButton(
                master=self.temp_label, text="X", width=20, height=20, font=(
                    "Arial", 30), corner_radius=15, command=lambda: (
                    self.destroy_weather()))
            self.closetemp_button.grid(
                row=0, column=1, padx=10, pady=10, sticky="ne")
            # Set exists to true
            self.weather_exists = True
        else:
            # If the frame does not exist, create the frame and labels
            self.frame_weather = customtkinter.CTkFrame(
                master=self.frame_map, corner_radius=15, fg_color=None)
            self.frame_weather.grid(
                row=0, column=0, padx=5, pady=5, sticky="nw")
            self.temp_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=f"{self.temp}°C",
                text_color="#db2518",
                width=100,
                corner_radius=15,
                font=(
                    "Helvetica",
                    30))
            self.temp_label.grid(
                row=0, column=0, padx=5, pady=5, sticky="nesw")
            self.weather_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=self.weather.title(),
                text_color="#db2518",
                width=100,
                corner_radius=15,
                font=(
                    "Helvetica",
                    25))
            self.weather_label.grid(
                row=1, column=0, padx=5, pady=5, sticky="nesw")
            self.tempmin_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=f"min: {self.temp_min}°C",
                text_color="#9e2c2c",
                corner_radius=15,
                font=(
                    "Helvetica",
                    15))
            self.tempmin_label.grid(
                row=2, column=0, padx=5, pady=5, sticky="nesw")
            self.tempmax_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=f"min: {self.temp_max}°C",
                text_color="#9e2c2c",
                corner_radius=15,
                font=(
                    "Helvetica",
                    15))
            self.tempmax_label.grid(
                row=3, column=0, padx=5, pady=5, sticky="nesw")
            self.sunrise_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=f"Sunrise: {self.sunrisetext}",
                text_color="#9e2c2c",
                corner_radius=15,
                font=(
                    "Helvetica",
                    15))
            self.sunrise_label.grid(
                row=4, column=0, padx=5, pady=5, sticky="nesw")
            self.sunset_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=f"Sunset: {self.sunsettext}",
                text_color="#9e2c2c",
                corner_radius=15,
                font=(
                    "Helvetica",
                    15))
            self.sunset_label.grid(
                row=5, column=0, padx=5, pady=5, sticky="nesw")
            self.location_label = customtkinter.CTkLabel(
                master=self.frame_weather,
                text=f"{self.city}, {self.country}",
                text_color="#9e2c2c",
                corner_radius=15,
                font=(
                    "Helvetica",
                    15))
            self.location_label.grid(
                row=6, column=0, padx=5, pady=5, sticky="nesw")
            self.closetemp_button = customtkinter.CTkButton(
                master=self.temp_label, text="X", width=20, height=20, font=(
                    "Arial", 30), corner_radius=15, command=lambda: (
                    self.destroy_weather()))
            self.closetemp_button.grid(
                row=0, column=1, padx=10, pady=10, sticky="ne")
            # Set exists to true
            self.weather_exists = True

    def destroy_advice(self):
        # Destroy the label and button
        self.advice_label.destroy()
        self.closeaqi_button.destroy()
        # Set exists to false
        self.advice_exists = False

    def destroy_weather(self):
        # Destroy the frame
        self.frame_weather.destroy()
        # Set exists to false
        self.weather_exists = False

    def aqi_db(self, lat: float, lon: float, aqi: int):
        # Connect to the database
        conn = sqlite3.connect("Database.db")
        # Set database cursor
        c = conn.cursor()
        # Execute SQL command to create a table if it does not already exists
        # called 'AQIRequests' with the data, lat, lon and aqi
        c.execute('''
                  CREATE TABLE IF NOT EXISTS AQIRequests(
                  requestID INTEGER PRIMARY KEY AUTOINCREMENT,
                  Lat FLOAT,
                  Lon FLOAT,
                  AQI INTEGER
        )''')

        data = "INSERT INTO AQIRequests(Lat, Lon, AQI) VALUES(?,?,?)"
        # Execute SQL command to insert data and create an entry in the
        # 'AQIRequests' table with the values of the lat, lon and aqi
        c.execute(data, (lat, lon, aqi))

        conn.commit()
        print(f"Request stored in database({lat}, {lon}, {aqi})")

    def weather_db(self, lat: float, lon: float, temp: float, weather: str):
        # Connect to the database
        conn = sqlite3.connect("Database.db")
        # Set database cursor
        c = conn.cursor()
        # Execute SQL command to create a table if it does not already exists
        # called 'WeatherRequests' with the data, lat, lon, temp and weather
        c.execute('''
                  CREATE TABLE IF NOT EXISTS WeatherRequests(
                  requestID INTEGER PRIMARY KEY AUTOINCREMENT,
                  Lat FLOAT,
                  Lon FLOAT,
                  Temp FLOAT,
                  Weather STRING
        )''')

        data = "INSERT INTO WeatherRequests(Lat, Lon, Temp, Weather) VALUES(?,?,?,?)"
        # Execute SQL command to insert data and create an entry in the
        # 'WeatherRequests' table with the values of the lat, lon, temp and
        # weather
        c.execute(data, (lat, lon, temp, weather))

        conn.commit()
        print(f"Request stored in database({lat}, {lon}, {temp}°C, {weather})")

    def settings(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # Create and configure CTk Frames
        self.frame_header = customtkinter.CTkFrame(
            master=self, corner_radius=15, fg_color=None)
        self.frame_header.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="nesw")

        self.frame_header.grid_rowconfigure(0, weight=1)
        self.frame_header.grid_columnconfigure(0, weight=1)

        self.frame_settings = customtkinter.CTkFrame(
            master=self, corner_radius=15, fg_color=None)
        self.frame_settings.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="nw")

        self.frame_settings.grid_rowconfigure(0, weight=1)
        self.frame_settings.grid_columnconfigure(0, weight=1)
        # Header Frame
        # Create header widgets
        self.settings_label = customtkinter.CTkLabel(
            master=self.frame_header, text="Settings", width=280, height=120, font=(
                "Arial", 30), corner_radius=15, fg_color="transparent", anchor="w")
        self.settings_label.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="nesw")

        self.return_image = customtkinter.CTkImage(
            Image.open(
                os.path.join(
                    self.image_path, "return_icon.png")), size=(
                100, 100))

        self.return_button = customtkinter.CTkButton(
            master=self.frame_header,
            text="Back",
            width=180,
            height=120,
            font=(
                "Arial",
                30),
            corner_radius=15,
            image=self.return_image,
            anchor="w",
            command=lambda: (
                self.destroy_children(),
                self.dashboard()))
        self.return_button.grid(
            row=0,
            column=1,
            padx=10,
            pady=10,
            sticky="nesw")
        # Settings Frame
        # Create settings widgets
        self.darkmode_switch = customtkinter.CTkSwitch(
            self.frame_settings,
            text="Dark Mode",
            command=lambda: self.change_appearance(
                self.new_mode.get()),
            variable=self.new_mode,
            onvalue="Dark",
            offvalue="Light")
        self.darkmode_switch.grid(row=0, padx=5, pady=5)

        self.tile_label = customtkinter.CTkLabel(
            self.frame_settings,
            text="Change Map Tiles: ",
            width=280,
            height=120,
            corner_radius=15,
            fg_color="transparent",
            anchor="w")
        self.tile_label.grid(row=1, column=0, padx=5, pady=5)

        self.tile_option_menu = customtkinter.CTkOptionMenu(
            self.frame_settings,
            values=[
                "OpenStreetMap",
                "Google Maps",
                "Google Earth",
                "Black & White"],
            command=self.change_map_value)
        self.tile_option_menu.grid(row=1, column=1, padx=5, pady=5)

        self.theme_label = customtkinter.CTkLabel(
            self.frame_settings,
            text="Change Theme: ",
            width=280,
            height=120,
            corner_radius=15,
            fg_color="transparent",
            anchor="w")
        self.theme_label.grid(row=2, padx=5, pady=5)

        self.theme_option_menu = customtkinter.CTkOptionMenu(
            self.frame_settings, values=[
                "Blue", "Dark Blue", "Green"], command=self.change_theme)
        self.theme_option_menu.grid(row=2, column=1, padx=5, pady=5)

    def change_appearance(self, new_mode: str):
        # Set appearance mode to value inputted from option menu
        if new_mode == "Dark":
            customtkinter.set_appearance_mode("dark")
        elif new_mode == "Light":
            customtkinter.set_appearance_mode("light")
        else:
            customtkinter.set_appearance_mode("system")

    def change_map_value(self, new_map: str):
        # Set the map_value StringVar to value inputted from option menu
        self.map_value = customtkinter.StringVar(value=new_map)

    def change_theme(self, new_theme: str):
        # Set colour theme to value inputted from option menu
        if new_theme == "Blue":
            customtkinter.set_default_color_theme("blue")
        if new_theme == "Dark Blue":
            customtkinter.set_default_color_theme("dark-blue")
        if new_theme == "Green":
            customtkinter.set_default_color_theme("green")

    def health_tracker(self):
        # Reset default values
        self.MET = 2.8
        self.speed = 0.9
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # Create and configure CTk Frames
        self.frame_header = customtkinter.CTkFrame(
            master=self, corner_radius=15, fg_color=None)
        self.frame_header.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="nesw")

        self.frame_header.grid_rowconfigure(0, weight=1)
        self.frame_header.grid_columnconfigure(0, weight=1)

        self.frame_tracker = customtkinter.CTkFrame(
            master=self, corner_radius=15, fg_color=None)
        self.frame_tracker.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="nw")

        self.frame_tracker.grid_rowconfigure(0, weight=1)
        self.frame_tracker.grid_columnconfigure(0, weight=1)
        # Header Frame
        # Create header widgets
        self.tracker_label = customtkinter.CTkLabel(
            master=self.frame_header, text="Health Tracker", width=100, height=120, font=(
                "Arial", 30), corner_radius=15, fg_color="transparent", anchor="w")
        self.tracker_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.return_image = customtkinter.CTkImage(
            Image.open(
                os.path.join(
                    self.image_path, "return_icon.png")), size=(
                100, 100))

        self.return_button = customtkinter.CTkButton(
            master=self.frame_header,
            text="Back",
            width=180,
            height=120,
            font=(
                "Arial",
                30),
            corner_radius=15,
            image=self.return_image,
            anchor="e",
            command=lambda: (
                self.destroy_children(),
                self.dashboard()))
        self.return_button.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        # Tracker Frame
        # Create health tracker widgets
        self.weight_label = customtkinter.CTkLabel(
            self.frame_tracker,
            text="Please enter your weight (kg) ",
            corner_radius=15,
            fg_color="transparent",
            anchor="w")
        self.weight_label.grid(row=0, column=0, padx=5, pady=5)

        self.entry_weight = customtkinter.CTkEntry(
            master=self.frame_tracker, placeholder_text="e.g 67", width=200)
        self.entry_weight.grid(row=0, column=1, padx=5, pady=5)

        self.height_label = customtkinter.CTkLabel(
            self.frame_tracker,
            text="Please enter your height (m) ",
            corner_radius=15,
            fg_color="transparent",
            anchor="w")
        self.height_label.grid(row=1, column=0, padx=5, pady=5)

        self.entry_height = customtkinter.CTkEntry(
            master=self.frame_tracker, placeholder_text="e.g 1.7")
        self.entry_height.grid(row=1, column=1, padx=5, pady=5)

        self.steps_label = customtkinter.CTkLabel(
            self.frame_tracker,
            text="Please enter your steps taken",
            corner_radius=15,
            fg_color="transparent",
            anchor="w")
        self.steps_label.grid(row=2, column=0, padx=5, pady=5)

        self.entry_steps = customtkinter.CTkEntry(
            master=self.frame_tracker, placeholder_text="e.g 10000", width=200)
        self.entry_steps.grid(row=2, column=1, padx=5, pady=5)

        self.speed_label = customtkinter.CTkLabel(
            self.frame_tracker,
            text="Select a speed",
            corner_radius=15,
            fg_color="transparent")
        self.speed_label.grid(row=3, column=0, padx=5, pady=5)

        self.speed_option_menu = customtkinter.CTkOptionMenu(
            self.frame_tracker, values=[
                "Slow", "Average", "Fast"], command=self.change_speed_value)
        self.speed_option_menu.grid(row=3, column=1, padx=5, pady=5)

        self.display_speed_label = customtkinter.CTkLabel(
            self.frame_tracker,
            text="2 miles/hour (3.2 km/h)",
            corner_radius=15,
            fg_color="transparent")
        self.display_speed_label.grid(row=4, column=1, padx=5, pady=5)

        self.calculate_button = customtkinter.CTkButton(
            master=self.frame_tracker,
            text="Calculate Calories Lost",
            corner_radius=15,
            command=lambda: self.calculate_calories())
        self.calculate_button.grid(row=5, column=0, padx=5, pady=5)

        self.calories_label = customtkinter.CTkLabel(
            self.frame_tracker,
            text="0 calories lost",
            corner_radius=15,
            fg_color="transparent")
        self.calories_label.grid(row=5, column=1, padx=5, pady=5)

        self.error_label = customtkinter.CTkLabel(
            self.frame_tracker,
            text="",
            corner_radius=15,
            fg_color="transparent",
            text_color="#c92a2a")
        self.error_label.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    def change_speed_value(self, new_speed: str):
        # Set speed values depending on new_speed (option menu value)
        if new_speed == "Slow":
            self.display_speed_label.configure(text="2 miles/hour (0.9 m/s)")
            self.MET = 2.8
            self.speed = 0.9
        if new_speed == "Average":
            self.display_speed_label.configure(text="3 miles/hour (1.34 m/s)")
            self.MET = 3.5
            self.speed = 1.34
        if new_speed == "Fast":
            self.display_speed_label.configure(text="4 miles/hour (1.79 m/s)")
            self.MET = 5
            self.speed = 1.79

    def calculate_calories(self):
        # Input check that displays the input needs to be changed when
        # ValueError is present using a try except
        try:
            # Calculation from: https://www.omnicalculator.com/sports/steps-to-calories
            # Calorie calculator, You need to know your weight in kilograms, height in meters, how many steps you've taken,
            # and your pace in m/s. You can stick to the general pace values and their MET cofactors:
            #
            # Slow - 0.9 m/s (2.8 MET);
            # Average - 1.34 m/s (3.5 MET);
            # Fast - 1.79 m/s (5 MET).
            # Use the following formula to calculate the stride and the walked distance.
            # MET: The ratio of the work metabolic rate to the resting
            # metabolic rate. One MET is defined as 1 kcal/kg/hour

            # Sometimes the calories burned at a slow pace will be higher than that of a faster rate, this is because
            # we calculate the maintenance calories as walking 10000 steps at a slow pace compared to a average pace would
            # take a longer amount of time meaning more maintenance calories
            # would be burned
            stride = float(self.entry_height.get()) * 0.414
            distance = stride * float(self.entry_steps.get())
            time = distance / self.speed
            calories = time * self.MET * 3.5 * \
                float(self.entry_weight.get()) / (200 * 60)
            # Configure label text
            self.calories_label.configure(
                text=f"{int(calories)} calories lost")
            self.error_label.configure(text="")
        except ValueError:
            # If ValueError configure label text to display error
            self.error_label.configure(
                text="Please enter a valid input, only integers and floats.")

    def on_closing(self, event=0):
        # Destroy window
        self.destroy()

    def destroy_children(self):
        # Destroy all children of self (widgets and frames present in the
        # window)
        for child in self.winfo_children():
            child.destroy()

    def start(self):
        # Main loop/Create window
        self.mainloop()


# Check if program is the main program to be executed
if __name__ == '__main__':
    # Initialize object
    app = App()
    # Run object start function
    app.start()
