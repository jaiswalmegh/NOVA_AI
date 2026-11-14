
import requests

from config.settings import WEATHER_API_KEY


class WeatherTool:

    def __init__(self):

        self.api_key = WEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.timeout = 15

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": "NOVA-AI/2.0"
        })

    # =========================================
    # GET WEATHER
    # =========================================

    def get_weather(self, city, units="metric"):

        if not isinstance(city, str) or not city.strip():

            return self._error(
                "Please provide a valid city name."
            )

        if not self.api_key:

            return self._error(
                "Weather API key is missing. Add WEATHER_API_KEY to your .env file."
            )

        if units not in ("metric", "imperial"):

            units = "metric"

        try:

            response = self.session.get(
                self.base_url,
                params={
                    "q": city.strip(),
                    "appid": self.api_key,
                    "units": units
                },
                timeout=self.timeout
            )

            if response.status_code == 404:

                return self._error(
                    "City not found. Please check the city name."
                )

            if response.status_code == 401:

                return self._error(
                    "Invalid weather API key."
                )

            if response.status_code == 429:

                return self._error(
                    "Weather API rate limit reached. Try again later."
                )

            response.raise_for_status()

            weather_data = response.json()

            main_data = weather_data["main"]

            weather_info = weather_data["weather"][0]

            wind_data = weather_data.get("wind", {})

            sys_data = weather_data.get("sys", {})

            temperature_unit = (
                "°C" if units == "metric" else "°F"
            )

            wind_unit = (
                "m/s" if units == "metric" else "mph"
            )

            result = {

                "city": weather_data.get("name", city),

                "country": sys_data.get("country", ""),

                "temperature": main_data.get("temp"),

                "feels_like": main_data.get("feels_like"),

                "minimum_temperature": main_data.get("temp_min"),

                "maximum_temperature": main_data.get("temp_max"),

                "humidity": main_data.get("humidity"),

                "pressure": main_data.get("pressure"),

                "condition": weather_info.get("main"),

                "description": weather_info.get("description"),

                "wind_speed": wind_data.get("speed"),

                "wind_unit": wind_unit,

                "cloudiness": weather_data.get(
                    "clouds", {}
                ).get("all"),

                "visibility": weather_data.get("visibility"),

                "sunrise": sys_data.get("sunrise"),

                "sunset": sys_data.get("sunset"),

                "temperature_unit": temperature_unit,

                "units": units
            }

            return {

                "success": True,

                "message": "Weather information retrieved successfully.",

                "data": result

            }

        except requests.Timeout:

            return self._error(
                "Weather service request timed out."
            )

        except requests.ConnectionError:

            return self._error(
                "Unable to connect to the weather service. Check your internet connection."
            )

        except requests.HTTPError as error:

            print(f"Weather HTTP Error: {error}")

            return self._error(
                "Weather service returned an HTTP error."
            )

        except requests.RequestException as error:

            print(f"Weather API Error: {error}")

            return self._error(
                "Unable to connect to the weather service."
            )

        except (KeyError, IndexError, ValueError, TypeError) as error:

            print(f"Weather Data Error: {error}")

            return self._error(
                "Unable to process weather information."
            )

    # =========================================
    # ERROR RESPONSE
    # =========================================

    def _error(self, message):

        return {
            "success": False,
            "message": message,
            "data": None
        }

    # =========================================
    # CLOSE SESSION
    # =========================================

    def close(self):

        self.session.close()
