# MomentInMotion

![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)

A personal activity suggestion web application that recommends activities based on your location, current weather, and personal interests. Powered by real-time weather data and generative AI for personalized suggestions.


## Features

- **User Accounts**: Secure sign-up and login to save preferences
- **User Metadata**: Track personal interests and driving ability
- **Real-Time Weather**: Fetches current weather data based on location
- **AI-Powered Suggestions**: Personalized activity recommendations using Gemini AI
- **Asynchronous Experience**: Non-blocking weather fetching for smooth user interaction

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/brar-karamjit/MomentInMotion.git
   cd MomentInMotion
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory and add your API keys:
   ```
   OPENWEATHER_API_KEY=your_openweather_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

5. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000` in your browser.

## Docker Setup

Alternatively, you can run the application using Docker:

1. **Ensure Docker is installed** on your system.

2. **Build the Docker image**:
   ```bash
   docker build -t momentinmotion .
   ```

3. **Run the Docker container**:
   ```bash
   docker run -p 8000:8000 --env-file .env momentinmotion
   ```

   Or, if you prefer to pass environment variables directly:
   ```bash
   docker run -p 8000:8000 -e OPENWEATHER_API_KEY=your_key -e GEMINI_API_KEY=your_key momentinmotion
   ```

   Visit `http://127.0.0.1:8000` in your browser.

## Usage

1. Register a new account or log in with existing credentials.
2. Update your profile with interests and preferences.
3. Allow location access for weather-based suggestions.
4. Receive personalized activity recommendations tailored to current conditions.

## Technologies Used

- **Backend**: Django (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **APIs**:
  - Open-Meteo for weather data
  - Google Gemini AI for activity suggestions
- **Other**: python-dotenv for environment management


## Project Structure

```
MomentInMotion/
├── core/                    # Main Django app
│   ├── migrations/          # Database migrations
│   ├── static/              # Static files (CSS, JS, images)
│   ├── templates/           # HTML templates
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   └── urls.py              # URL routing
├── MomentInMotion/          # Django project settings
│   ├── settings.py          # Project configuration
│   └── urls.py              # Main URL configuration
├── Dockerfile               # Docker configuration
├── .dockerignore            # Docker ignore file
├── db.sqlite3               # SQLite database
├── manage.py                # Django management script
└── requirements.txt         # Python dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.