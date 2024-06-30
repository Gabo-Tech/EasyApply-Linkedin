import unittest
from unittest.mock import patch, MagicMock
from easy_apply_linkedin import EasyApplyLinkedin

class TestEasyApplyLinkedin(unittest.TestCase):
    def setUp(self):
        self.data = {
            "email": "sendmessage@gabo.email",
            "password": "bp8v9fvk#?QaKe7",
            "keywords": ["TypeScript", "Angular", "React"],
            "keywordsToAvoid": ["C++", ".NET"],
            "locations": ["Switzerland", "Belgium"],
            "driver_path": "/usr/local/bin/geckodriver",
            "sortBy": "R",
            "filters": {
                "easy_apply": True,
                "experience": [],
                "jobType": ["Full-time", "Contract"],
                "timePostedRange": [],
                "workplaceType": ["Remote", "Hybrid"],
                "less_than_10_applicants": False
            }
        }
        self.bot = EasyApplyLinkedin(self.data)

    @patch('easy_apply_linkedin.webdriver.Firefox')
    def test_login_linkedin(self, MockWebDriver):
        mock_driver = MockWebDriver.return_value
        mock_driver.find_element.return_value = MagicMock()
        self.bot.login_linkedin()
        mock_driver.get.assert_called_with("https://www.linkedin.com/login")
        self.assertTrue(mock_driver.find_element.called)

    @patch('easy_apply_linkedin.webdriver.Firefox')
    def test_construct_url(self, MockWebDriver):
        url = self.bot.construct_url()
        self.assertIn("keywords=TypeScript%20OR%20Angular%20OR%20React", url)
        self.assertIn("geoId=106693272", url)
        self.assertIn("f_AL=true", url)

    @patch('easy_apply_linkedin.webdriver.Firefox')
    def test_apply_filters_and_search_no_results(self, MockWebDriver):
        mock_driver = MockWebDriver.return_value
        mock_driver.find_element.side_effect = NoSuchElementException
        self.bot.apply_filters_and_search()
        self.assertEqual(self.bot.current_location_index, 1)

    @patch('easy_apply_linkedin.webdriver.Firefox')
    def test_log_error(self, MockWebDriver):
        self.bot.log_error("Test error")
        errors = self.bot.load_json(self.bot.ERROR_LOG_PATH)
        self.assertTrue(any("Test error" in v for v in errors.values()))

if __name__ == "__main__":
    unittest.main()
