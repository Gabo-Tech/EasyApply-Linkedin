# EasyApply-Linkedin

With this tool, you can easily automate the process of applying for jobs on LinkedIn!

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

1. Install Selenium. Use `pip` to install the Selenium package:
    ```sh
    pip install selenium
    ```

2. Selenium requires a driver to interface with the chosen browser. Make sure the driver is in your path, you will need to add your `driver_path` to the `config.json` file.

    I used the Firefox driver, you can download it [here](https://github.com/mozilla/geckodriver/releases). You can also download drivers for [Chrome](https://sites.google.com/a/chromium.org/chromedriver/downloads), [Edge](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/), or [Safari](https://webkit.org/blog/6900/webdriver-support-in-safari-10/), depending on your preferred browser.

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Gabo-Tech/EasyApply-Linkedin.git
    cd EasyApply-Linkedin
    ```

2. Install the necessary packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Update the `config.json` file with your information:
    ```json
    {
        "email": "example@example.com",
        "password": "securePassword123!",
        "keywords": ["Web Developer", "JavaScript", "React"],
        "keywordsToAvoid": ["C++", ".NET"],
        "locations": ["New York", "Los Angeles", "San Francisco"],
        "driver_path": "/usr/local/bin/geckodriver",
        "sortBy": "R",
        "filters": {
            "easy_apply": true,
            "experience": ["Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"],
            "jobType": ["Full-time", "Part-time", "Contract", "Internship", "Temporary"],
            "timePostedRange": ["Any Time", "Last Month", "Past Week", "Past 24 hours"],
            "workplaceType": ["Remote", "Hybrid", "On-site"],
            "less_than_10_applicants": true
        }
    }
    ```

4. Update the location codes in the script:
    ```python
    LOCATION_MAPPING = {
        "Canada": "101174742",
        "Portugal": "100364837",
        "Switzerland": "106693272",
        "United States": "103644278",
        "Belgium": "100565514",
        "Netherlands": "102890719",
        "DACH": "91000006",
        "Benelux": "91000005",
        "European Union": "91000000",
        "European Economic Area": "91000002",
        "Germany": "101282230",
        "Spain": "105646813",
        "United Kingdom": "101165590"
    }
    ```
    You can find the code in the `geoId` found in the LinkedIn URL after doing a job search. These are the correct ones if you don't want to search elsewhere, but there are many more.

### Usage

1. Run the application:
    ```sh
    python main.py
    ```

### Features

- **Automated Job Applications**: Automatically apply to jobs that match your keywords and location.
- **Filter Options**: Customize filters for experience level, job type, time posted, workplace type, and more.
- **Logging**: Keep track of errors and the companies you've applied to.

### Customization

You can customize the job search and application process by editing the `config.json` file:
- **email**: Your LinkedIn email address.
- **password**: Your LinkedIn password.
- **keywords**: Keywords for finding specific job titles (e.g., "Machine Learning Engineer", "Data Scientist").
- **keywordsToAvoid**: Keywords to exclude from your search.
- **locations**: Locations where you are currently looking for a position.
- **driver_path**: Path to your downloaded WebDriver.
- **sortBy**: Sort order for job listings.
- **filters**: Various filters to narrow down the job search (e.g., easy apply, experience level, job type, etc.).

### Testing

#### Unit Tests

Unit tests mock the Selenium WebDriver to test methods in isolation without making actual web requests.

Run the unit tests:
```bash
python unit_tests.py
```

#### E2E Tests

End-to-end tests using `pytest` and `selenium` require an actual web browser to run.

Run the E2E tests:
```bash
pytest e2e_tests.py
```

### Contributing

Please feel free to comment or give suggestions/issues. Fork and submit pull requests for any enhancements or bug fixes.

### License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Gabo-Tech/EasyApply-Linkedin/blob/master/LICENCE) file for details.