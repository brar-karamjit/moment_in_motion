from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import requests
import os
import logging

from .forms import UserProfileForm
from core.models import UserMetadata    


# helper for hello microservice
HELLO_SERVICE_URL = os.getenv(
    "HELLO_SERVICE_URL",
    "http://hello-service.hello.svc.cluster.local",
)




GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # stored in environment variable
logger = logging.getLogger(__name__)
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
        temperature = request.POST.get("temperature")
        weathercode = request.POST.get("weathercode")

        weather = {"temperature": temperature, "weathercode": weathercode}

        suggestion_data = get_suggestion(user, metadata, weather, lat, lon)
        request.session["last_suggestion"] = suggestion_data
        return redirect("home")

    return render(request, "core/home.html", {
        "user": user,
        "suggestion_data": suggestion_data,
    })


@login_required
def call_hello(request):
    """Invoke the lightweight hello microservice and render its response."""
    try:
        resp = requests.get(HELLO_SERVICE_URL, timeout=3)
        hello_text = resp.text.strip()
    except requests.RequestException as exc:
        logger.warning("hello service unreachable", exc_info=exc)
        hello_text = "(failed to contact hello service)"

    return JsonResponse({"hello": hello_text})


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