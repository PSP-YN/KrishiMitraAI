import unittest
from main import weather_conflict_detected


class WeatherConflictGuardTests(unittest.TestCase):
    def test_rejects_explicit_no_rain_claim_against_positive_rainfall(self):
        self.assertTrue(weather_conflict_detected("No rain is expected this week.", 34.8))

    def test_rejects_dry_forecast_claim_against_positive_rainfall(self):
        self.assertTrue(weather_conflict_detected("The forecast indicates a dry period.", 12.0))

    def test_accepts_neutral_monitoring_language(self):
        self.assertFalse(weather_conflict_detected("Monitor field drainage and verify local rainfall.", 34.8))

    def test_zero_rainfall_does_not_trigger_guard(self):
        self.assertFalse(weather_conflict_detected("No rain is forecast.", 0.0))

    def test_rejects_explicit_zero_rainfall_claim_when_total_is_positive(self):
        self.assertTrue(weather_conflict_detected("Rainfall will be 0 mm.", 2.0))


if __name__ == "__main__":
    unittest.main()
