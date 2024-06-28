# EasyApply-Linkedin

With this tool, you can easily automate the process of applying for jobs on LinkedIn!

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

1. Install selenium. I used `pip` to install the selenium package.
    ```sh
    pip install selenium
    ```

2. Selenium requires a driver to interface with the chosen browser. Make sure the driver is in your path, you will need to add your `driver_path` to the `config.json` file.

    I used the Chrome driver, you can download it [here](https://sites.google.com/a/chromium.org/chromedriver/downloads). You can also download drivers for [Edge](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/), [Firefox](https://github.com/mozilla/geckodriver/releases), or [Safari](https://webkit.org/blog/6900/webdriver-support-in-safari-10/), depending on your preferred browser.

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your_username/easyapply-linkedin.git
    cd easyapply-linkedin
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
        "locations": ["New York", "Los Angeles", "San Francisco"],
        "driver_path": "/usr/local/bin/chromedriver",
        "sortBy": "Alphabetical",
        "filters": {
            "easy_apply": true,
            "experience": ["Internship", "Entry Level", "Associate", "Mid-Senior Level", "Director", "Executive"], 
            "jobType": ["Full-Time", "Part-Time", "Contract", "Internship", "Temporary"], 
            "timePostedRange": ["Any Time", "Last Month", "Past Week", "Past 24 Hours"], 
            "workplaceType": ["Remote", "Hybrid", "On-site"],
            "less_than_10_applicants": true, 
            "commitments": ["Full-Time", "Part-Time", "Contract", "Temporary", "Volunteer"] 
        },
        "experience": [
            {
                "title": "Junior Web Developer",
                "description": "Developing responsive web applications using JavaScript and React.",
                "date": "Jan 2023 - Present",
                "company": "Example Company"
            }
        ],
        "projects": [
            {
                "title": "Project Alpha",
                "desc": "A project description here...",
                "link": "#",
                "skills": ["JavaScript", "React", "Node.js"]
            }
        ],
        "skills": [
            "JavaScript",
            "React",
            "Node.js",
            "Express",
            "MongoDB"
        ],
        "user_inputs": {}
    }
    ```

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
- **locations**: Locations where you are currently looking for a position.
- **driver_path**: Path to your downloaded WebDriver.
- **sortBy**: Sort order for job listings.
- **filters**: Various filters to narrow down the job search (e.g., easy apply, experience level, job type, etc.).

### Contributing

Please feel free to comment or give suggestions/issues. Fork and submit pull requests for any enhancements or bug fixes.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
