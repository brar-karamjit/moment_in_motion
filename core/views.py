from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import requests
import os
import logging

from .forms import UserProfileForm
from core.models import UserMetadata


# helper for weather microservice
WEATHER_SERVICE_URL = (
    os.getenv("WEATHER_SERVICE_URL")
    or os.getenv("HELLO_SERVICE_URL")
    or "http://weather-service.weather"
)
WEATHER_API_URL = f"{WEATHER_SERVICE_URL.rstrip('/')}/weather"



GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # stored in environment variable
logger = logging.getLogger(__name__)


def fetch_weather_from_service(latitude, longitude, timeout=5):
    try:
        resp = requests.get(
            WEATHER_API_URL,
            params={"lat": latitude, "lon": longitude},
            timeout=timeout,
        )
    except requests.RequestException as exc:
        logger.warning("weather service unreachable", exc_info=exc)
        return None, "Unable to reach weather service", 503

    try:
        payload = resp.json()
    except ValueError:
        payload = {}

    if resp.status_code >= 400:
        api_error = payload.get("error") if isinstance(payload, dict) else None
        return None, api_error or "Weather lookup failed", resp.status_code

    if not isinstance(payload, dict) or "current_weather" not in payload:
        return None, "Invalid weather response from weather service", 502

    return payload, None, 200


def get_suggestion(user, metadata, weather, latitude, longitude):
    user_name = f"{user.first_name} {user.last_name}".strip() or user.username or "Explorer"
    interests = getattr(metadata, "interests", None) or "no specific interest"
    drives = getattr(metadata, "drives", None) or "unspecified"

    prompt_text = f"""
    User: {user_name}
    Interests: {interests}
    Drives: {drives}
    Latitude: {latitude}
    Longitude: {longitude}
    Weather: {weather['temperature']}°C, {weather.get('weathercode', 'unknown')}
    Calculate the rough city name from given latitute longitude.
    Important: Keep your answer very brief. For example, "Visit the local museum" or "Go for a walk in the park (park name)". 
    You can also suggest acitivies outside user interest, take various factors into account like weather, time of day, events happening in city.
    Suggest activities this user can do right now.
    """

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {"Content-Type": "application/json", "X-goog-api-key": GEMINI_API_KEY}
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=12)
    except requests.RequestException as exc:
        logger.warning("Suggestion service unreachable", exc_info=exc)
        return {"response": "I couldn't reach our ideas service just now. Try again in a moment."}

    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            message = "We're a bit busy. Give it about {} seconds and try again.".format(retry_after)
        else:
            message = "We're experiencing a rush of requests right now. Please try again shortly."
        logger.info("Suggestion service rate limited the request (user=%s)", user.username)
        return {"response": message}

    if response.status_code >= 400:
        try:
            error_payload = response.json()
            api_message = error_payload.get("error", {}).get("message")
        except ValueError:
            api_message = None
        logger.warning(
            "Suggestion service returned error %s for user=%s", response.status_code, user.username
        )
        friendly_message = api_message or "Something went wrong fetching a suggestion. Please try again soon."
        return {"response": friendly_message}

    try:
        result = response.json()

        candidates = result.get("candidates", [])
        suggestion_text = ""
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                suggestion_text = parts[0].get("text", "").strip()

        return {"response": suggestion_text or "No suggestion available."}

    except (ValueError, KeyError) as exc:
        logger.error("Unexpected response from suggestion service", exc_info=exc)
        return {"response": "We received an unexpected response. Please try again soon."}


@login_required
def home(request):
    user = request.user
    try:
        metadata = UserMetadata.objects.get(user=user)
    except UserMetadata.DoesNotExist:
        metadata = None

    suggestion_data = request.session.pop("last_suggestion", None)
    city = "N/A"

    if request.method == "POST" and request.POST.get("action") == "get_suggestion":
        lat = request.POST.get("lat")
        lon = request.POST.get("lon")

        if lat is None or lon is None:
            suggestion_data = {"response": "Missing location data. Please allow location access and try again."}
            request.session["last_suggestion"] = suggestion_data
            return redirect("home")

        try:
            latitude = float(lat)
            longitude = float(lon)
        except ValueError:
            suggestion_data = {"response": "Invalid location values received. Please try again."}
            request.session["last_suggestion"] = suggestion_data
            return redirect("home")

        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            suggestion_data = {"response": "Location values are out of range. Please refresh and try again."}
            request.session["last_suggestion"] = suggestion_data
            return redirect("home")

        weather_payload, weather_error, _ = fetch_weather_from_service(latitude, longitude)
        if weather_error:
            suggestion_data = {"response": f"Could not retrieve weather via weather-service: {weather_error}"}
            request.session["last_suggestion"] = suggestion_data
            return redirect("home")

        current_weather = weather_payload.get("current_weather", {})
        weather = {
            "temperature": current_weather.get("temperature", "unknown"),
            "weathercode": current_weather.get("weathercode", "unknown"),
        }

        suggestion_data = get_suggestion(user, metadata, weather, latitude, longitude)
        request.session["last_suggestion"] = suggestion_data
        return redirect("home")

    return render(request, "core/home.html", {
        "user": user,
        "suggestion_data": suggestion_data,
    })


@login_required
def call_hello(request):
    """Invoke the lightweight weather microservice and render its response."""
    try:
        resp = requests.get(WEATHER_SERVICE_URL, timeout=3)
        hello_text = resp.text.strip()
    except requests.RequestException as exc:
        logger.warning("weather service unreachable", exc_info=exc)
        hello_text = "(failed to contact weather service)"

    return JsonResponse({"hello": hello_text})


@login_required
def call_weather(request):
    """Proxy weather lookup through weather-service."""
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    if lat is None or lon is None:
        return JsonResponse({"error": "Missing required query params: lat, lon"}, status=400)

    try:
        latitude = float(lat)
        longitude = float(lon)
    except ValueError:
        return JsonResponse({"error": "Invalid lat/lon. Values must be numeric."}, status=400)

    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return JsonResponse({"error": "lat/lon out of valid range"}, status=400)

    payload, error_message, status_code = fetch_weather_from_service(latitude, longitude)
    if error_message:
        return JsonResponse({"error": error_message}, status=status_code)

    return JsonResponse(payload)


@login_required
def profile(request):
    user = request.user
    try:
        metadata = UserMetadata.objects.get(user=user)
    except UserMetadata.DoesNotExist:
        metadata = UserMetadata(user=user)  # create blank metadata if missing

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=metadata)
        if form.is_valid():
            form.save()
            return redirect('profile')  # reload page after saving
    else:
        form = UserProfileForm(instance=metadata)

    return render(request, 'core/profile.html', {'form': form, 'user': user})