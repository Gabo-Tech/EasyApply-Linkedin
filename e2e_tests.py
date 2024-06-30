import pytest
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from easy_apply_linkedin import EasyApplyLinkedin

@pytest.fixture
def setup_browser():
    service = FirefoxService(executable_path="/usr/local/bin/geckodriver")
    driver = webdriver.Firefox(service=service)
    yield driver
    driver.quit()

@pytest.fixture
def setup_bot(setup_browser):
    data = {
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
    bot = EasyApplyLinkedin(data)
    bot.driver = setup_browser
    return bot

def test_login_linkedin(setup_bot):
    setup_bot.login_linkedin()
    assert "feed" in setup_bot.driver.current_url

def test_job_search(setup_bot):
    setup_bot.login_linkedin()
    setup_bot.job_search()
    assert "jobs/search" in setup_bot.driver.current_url

def test_find_offers(setup_bot):
    setup_bot.login_linkedin()
    setup_bot.job_search()
    setup_bot.find_offers()
    assert len(setup_bot.applied_companies) > 0

if __name__ == "__main__":
    pytest.main()
