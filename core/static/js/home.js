const weatherCodes = {
    0: "Clear",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Cloudy",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Heavy rain showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Severe thunderstorm"
};

const tempElement = document.getElementById("temperature");
const locationLabel = document.getElementById("location-label");
const windSpeedEl = document.getElementById("wind-speed");
const windDirectionEl = document.getElementById("wind-direction");
const lastUpdatedEl = document.getElementById("last-updated");

function showLoading() {
    if (tempElement) {
        tempElement.innerHTML = '<span class="loading">Pulling live telemetry</span>';
        tempElement.classList.remove("fade-in");
    }
}

function showError(message) {
    if (tempElement) {
        tempElement.innerHTML = `<span class="error">Telemetry error: ${message}</span>`;
        tempElement.classList.remove("fade-in");
    }
    if (locationLabel) {
        locationLabel.textContent = "Location unavailable";
    }
    [windSpeedEl, windDirectionEl, lastUpdatedEl].forEach((el) => {
        if (el) el.textContent = "--";
    });
}

function formatBearing(degrees) {
    if (typeof degrees !== "number" || Number.isNaN(degrees)) {
        return "--";
    }
    const directions = [
        "N",
        "NE",
        "E",
        "SE",
        "S",
        "SW",
        "W",
        "NW"
    ];
    const index = Math.round((degrees % 360) / 45) % 8;
    return `${directions[index]} (${Math.round(degrees)}°)`;
}

function formatUpdatedTime(timestamp) {
    if (!timestamp) return "--";
    try {
        const dt = new Date(timestamp);
        return dt.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    } catch (error) {
        console.warn("Unable to format time", error);
        return "--";
    }
}

async function updateLocationPill(lat, lon) {
    if (!locationLabel) return;
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=10&addressdetails=1`);
        const data = await response.json();
        if (data && data.address) {
            const city = data.address.city || data.address.town || data.address.village || data.address.hamlet;
            if (city) {
                locationLabel.textContent = city;
                return;
            }
        }
    } catch (error) {
        console.warn("Reverse geocoding failed:", error);
    }
    // Fallback to coordinates
    const formatted = `${lat.toFixed(2)}°, ${lon.toFixed(2)}°`;
    locationLabel.textContent = formatted;
}

function renderWeather(current) {
    if (!tempElement || !current) return;
    const temperature = Math.round(current.temperature);
    const code = current.weathercode;
    const windspeed = Math.round(current.windspeed);
    const winddirection = current.winddirection;
    const description = weatherCodes[code] || `Code ${code}`;

    tempElement.innerHTML = `
        <div class="weather-info fade-in">
            <div class="temp-large">${temperature}°C</div>
            <div class="weather-desc">${description}</div>
        </div>
    `;

    if (windSpeedEl) {
        windSpeedEl.textContent = `${windspeed} km/h`;
    }

    if (windDirectionEl) {
        windDirectionEl.textContent = formatBearing(winddirection);
    }

    if (lastUpdatedEl) {
        lastUpdatedEl.textContent = formatUpdatedTime(current.time);
    }

    const tempInput = document.getElementById("temperature_input");
    const weatherTextInput = document.getElementById("weather_text_input");
    if (tempInput) tempInput.value = temperature;
    if (weatherTextInput) weatherTextInput.value = description;
}

async function handlePositionSuccess(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    const latInput = document.getElementById("lat");
    const lonInput = document.getElementById("lon");
    if (latInput) latInput.value = lat;
    if (lonInput) lonInput.value = lon;

    await updateLocationPill(lat, lon);

    try {
        const resp = await fetch(`/weather/?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`);
        const data = await resp.json();

        if (!resp.ok) {
            const apiError = data && data.error ? data.error : `HTTP ${resp.status}`;
            throw new Error(apiError);
        }

        if (data && data.current_weather) {
            renderWeather(data.current_weather);
        } else {
            showError("Weather data missing");
        }
    } catch (err) {
        console.error("Weather fetch error:", err);
        showError(err && err.message ? err.message : "Unable to fetch weather data");
    }
}

function handlePositionError(error) {
    console.error("Geolocation error:", error);
    if (error.code === error.PERMISSION_DENIED) {
        showError("Location access denied. Enable geolocation to run weather inference.");
    } else {
        showError("Unable to determine location");
    }
}

// call weather-service when button clicked
const helloBtn = document.getElementById("call-hello");
const helloOutput = document.getElementById("hello-result");

if (helloBtn) {
    helloBtn.addEventListener("click", async (evt) => {
        evt.preventDefault();
        if (helloOutput) {
            helloOutput.innerHTML = '<span class="hello-loading">Probing service endpoint</span>';
        }

        try {
            const resp = await fetch("/hello/");
            if (!resp.ok) {
                throw new Error(`HTTP ${resp.status}`);
            }

            let message = "";
            try {
                const data = await resp.json();
                message = data.hello || "No message returned.";
            } catch (parseError) {
                const fallbackText = await resp.text();
                message = fallbackText || "No message returned.";
            }

            if (helloOutput) {
                helloOutput.innerHTML = `
                    <div class="hello-card fade-in">
                        <strong>Probe response</strong>
                        <div>${message}</div>
                        <div class="hello-meta">source: weather-service | path: /hello/</div>
                    </div>
                `;
            }
        } catch (err) {
            console.error("Error fetching service:", err);
            if (helloOutput) {
                helloOutput.textContent = "probe failed";
            }
        }
    });
}

if ("geolocation" in navigator && tempElement) {
    showLoading();
    navigator.geolocation.getCurrentPosition(handlePositionSuccess, handlePositionError, {
        enableHighAccuracy: false,
        timeout: 8000,
        maximumAge: 60_000
    });
} else if (tempElement) {
    showError("Geolocation is not supported by this browser");
}
