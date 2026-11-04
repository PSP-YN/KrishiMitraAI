import json
import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from main import app


class AdvisoryApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.weather = {
            "resolved_location": {"name": "Mysuru", "admin1": "Karnataka", "country": "India"},
            "current": {"temperature_2m": 22.0, "precipitation": 0.0},
            "daily": {
                "time": ["2026-11-04", "2026-11-05"],
                "precipitation_sum": [2.0, 3.0],
                "precipitation_probability_max": [40, 80],
                "temperature_2m_max": [28.0, 29.0],
                "temperature_2m_min": [18.0, 19.0],
            },
            "source": "Open-Meteo",
            "retrieved_at_utc": "2026-11-04T12:00:00+00:00",
        }
        self.payload = {
            "location": "Mysuru, Karnataka",
            "crop": "Ragi",
            "growth_stage": "Vegetative",
            "language": "English",
            "question": "What should I monitor?",
        }

    @patch("main.build_agent")
    @patch("main.get_weather_forecast")
    def test_success_returns_live_weather_and_agent_advisory(self, weather_tool, build_agent):
        weather_tool.return_value = json.dumps(self.weather)
        build_agent.return_value = Mock(return_value="Monitor soil moisture and consult local KVK officers.")

        response = self.client.post("/api/advisory", json=self.payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["agent_status"], "accepted")
        self.assertEqual(data["weather_source"], "Open-Meteo")
        self.assertEqual(data["weather"]["daily"]["time"], self.weather["daily"]["time"])
        self.assertEqual(data["weather_summary"]["precipitation_total_mm"], 5.0)
        self.assertIn("Monitor soil moisture", data["advisory"])
        build_agent.return_value.assert_called_once()

    @patch("main.build_agent")
    @patch("main.get_weather_forecast")
    def test_weather_failure_stops_before_model_execution(self, weather_tool, build_agent):
        weather_tool.return_value = json.dumps({"error": "No geocoding result"})

        response = self.client.post("/api/advisory", json=self.payload)

        self.assertEqual(response.status_code, 502)
        self.assertIn("No geocoding result", response.json()["detail"])
        build_agent.assert_not_called()

    @patch("main.build_agent")
    @patch("main.get_weather_forecast")
    def test_explicit_forecast_conflict_is_withheld(self, weather_tool, build_agent):
        weather_tool.return_value = json.dumps(self.weather)
        build_agent.return_value = Mock(return_value="No rain is expected this week.")

        response = self.client.post("/api/advisory", json=self.payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["agent_status"], "rejected_weather_conflict")
        self.assertIn("withheld", data["advisory"])
        self.assertIn("verified forecast", data["advisory"].lower())

    def test_unsupported_languages_are_rejected(self):
        for language in ("Hindi", "Kannada"):
            with self.subTest(language=language):
                response = self.client.post("/api/advisory", json={**self.payload, "language": language})
                self.assertEqual(response.status_code, 422)

    def test_whitespace_is_trimmed_before_validation(self):
        response = self.client.post("/api/advisory", json={**self.payload, "location": "  "})
        self.assertEqual(response.status_code, 422)

    @patch("main.requests.get")
    def test_health_reports_model_availability(self, get):
        result = Mock()
        result.json.return_value = {"models": [{"name": "qwen2.5:3b"}]}
        result.raise_for_status.return_value = None
        get.return_value = result

        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertTrue(response.json()["ollama_reachable"])
        self.assertTrue(response.json()["model_available"])

    @patch("main.requests.get")
    def test_health_reports_degraded_when_model_is_missing(self, get):
        result = Mock()
        result.json.return_value = {"models": []}
        result.raise_for_status.return_value = None
        get.return_value = result

        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "degraded")
        self.assertTrue(response.json()["ollama_reachable"])
        self.assertFalse(response.json()["model_available"])

    def test_frontend_assets_are_served(self):
        page = self.client.get("/")
        script = self.client.get("/static/app.js")
        stylesheet = self.client.get("/static/styles.css")
        self.assertEqual(page.status_code, 200)
        self.assertIn("/static/app.js", page.text)
        self.assertEqual(script.status_code, 200)
        self.assertEqual(stylesheet.status_code, 200)


if __name__ == "__main__":
    unittest.main()
