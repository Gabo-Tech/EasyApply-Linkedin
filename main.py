import json
import time
import urllib.parse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.firefox.service import Service as FirefoxService


class EasyApplyLinkedin:
    BASE_URL = "https://www.linkedin.com/jobs/search/"
    ERROR_LOG_PATH = Path("error_log.json")
    APPLIED_COMPANIES_LOG_PATH = Path("applied_companies_log.json")
    FAILED_APPLICATIONS_LOG_PATH = Path("failed_applications_log.json")

    TIME_POSTED_MAPPING = {
        "Any Time": "",
        "Last Month": "r2592000",
        "Past Week": "r604800",
        "Past 24 hours": "r86400",
    }

    EXPERIENCE_MAPPING = {
        "Internship": "1",
        "Entry level": "2",
        "Associate": "3",
        "Mid-Senior level": "4",
        "Director": "5",
        "Executive": "6",
    }

    WORKPLACE_TYPE_MAPPING = {
        "Remote": "2",
        "Hybrid": "3",
        "On-site": "1",
    }

    JOB_TYPE_MAPPING = {
        "Full-time": "F",
        "Part-time": "P",
        "Contract": "C",
        "Internship": "I",
        "Temporary": "T",
    }

    TITLE_MAPPING = {
        "Engineer": "9",
        "Developer": "25201",
        "Manager": "25170",
        "Specialist": "1456",
        "Consultant": "3731",
    }

    COMMITMENTS_MAPPING = {
        "Full-time": "1",
        "Part-time": "2",
        "Contract": "3",
        "Temporary": "4",
        "Volunteer": "5",
    }

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
        "United Kingdom": "101165590",
    }

    def __init__(self, data):
        """Initialize the EasyApplyLinkedin instance with user data."""
        self.email = data["email"]
        self.password = data["password"]
        self.keywords = " OR ".join(data["keywords"])
        self.keywords_to_avoid = " NOT ".join(data["keywordsToAvoid"])
        self.locations = data["locations"]
        self.filters = data["filters"]
        self.sort_by = data["sortBy"]
        self.context_data = data
        self.current_location_index = 0
        if "user_inputs" not in self.context_data:
            self.context_data["user_inputs"] = {}
        firefox_service = FirefoxService(executable_path=data["driver_path"])
        self.driver = webdriver.Firefox(service=firefox_service)
        self.init_logging()

    def init_logging(self):
        """Initialize logging for error and applied companies."""
        logging.basicConfig(level=logging.INFO)
        self.error_logger = logging.getLogger("ErrorLogger")
        self.applied_companies = self.load_json(self.APPLIED_COMPANIES_LOG_PATH)
        self.failed_applications = self.load_json(self.FAILED_APPLICATIONS_LOG_PATH)

    def load_json(self, path):
        """Load JSON data from the specified path."""
        if path.exists():
            with path.open("r") as file:
                return json.load(file)
        return {}

    def save_json(self, path, data):
        """Save JSON data to the specified path."""
        with path.open("w") as file:
            json.dump(data, file, indent=4)

    def log_error(self, error_msg):
        """Log error messages with a timestamp."""
        self.error_logger.error(error_msg)
        errors = self.load_json(self.ERROR_LOG_PATH)
        errors[str(datetime.now())] = error_msg
        self.save_json(self.ERROR_LOG_PATH, errors)
        self.cleanup_error_log()

    def log_info(self, message):
        """Log informational messages."""
        logging.info(message)

    def cleanup_error_log(self):
        """Clean up old error logs older than 1 day."""
        errors = self.load_json(self.ERROR_LOG_PATH)
        cutoff = datetime.now() - timedelta(days=1)
        errors = {k: v for k, v in errors.items() if datetime.fromisoformat(k) > cutoff}
        self.save_json(self.ERROR_LOG_PATH, errors)

    def log_applied_company(self, company):
        """Log the company to which an application was submitted."""
        self.applied_companies[company] = str(datetime.now())
        self.save_json(self.APPLIED_COMPANIES_LOG_PATH, self.applied_companies)
        self.cleanup_applied_companies_log()

    def cleanup_applied_companies_log(self):
        """Clean up logs of applied companies older than 2 weeks."""
        cutoff = datetime.now() - timedelta(weeks=2)
        self.applied_companies = {
            k: v
            for k, v in self.applied_companies.items()
            if datetime.fromisoformat(v) > cutoff
        }
        self.save_json(self.APPLIED_COMPANIES_LOG_PATH, self.applied_companies)

    def log_failed_application(self, company):
        """Log the company where application failed."""
        self.failed_applications[company] = str(datetime.now())
        self.save_json(self.FAILED_APPLICATIONS_LOG_PATH, self.failed_applications)
        self.cleanup_failed_applications_log()

    def cleanup_failed_applications_log(self):
        """Clean up logs of failed applications older than 2 weeks."""
        cutoff = datetime.now() - timedelta(weeks=2)
        self.failed_applications = {
            k: v
            for k, v in self.failed_applications.items()
            if datetime.fromisoformat(v) > cutoff
        }
        self.save_json(self.FAILED_APPLICATIONS_LOG_PATH, self.failed_applications)

    def login_linkedin(self):
        """Log in to LinkedIn using the provided credentials."""
        try:
            self.driver.get("https://www.linkedin.com/login")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "session_key"))
            )
            login_email = self.driver.find_element(By.NAME, "session_key")
            login_email.clear()
            login_email.send_keys(self.email)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "session_password"))
            )
            login_pass = self.driver.find_element(By.NAME, "session_password")
            login_pass.clear()
            login_pass.send_keys(self.password)
            login_pass.send_keys(Keys.RETURN)
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Jobs"))
            )
        except Exception as e:
            self.log_error(f"Login error: {e}")

    def job_search(self):
        """Perform job search based on keywords and locations."""
        while self.current_location_index < len(self.locations):
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "Jobs"))
                )
                jobs_link = self.driver.find_element(By.LINK_TEXT, "Jobs")
                jobs_link.click()
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")
                    )
                )
                search_keywords = self.driver.find_element(
                    By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']"
                )
                search_keywords.clear()
                search_keywords.send_keys(self.keywords)
                search_keywords.send_keys(" NOT ")
                search_keywords.send_keys(self.keywords_to_avoid)
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[aria-label='City, state, or zip code']")
                    )
                )
                search_location = self.driver.find_element(
                    By.CSS_SELECTOR, "input[aria-label='City, state, or zip code']"
                )
                search_location.clear()
                search_location.send_keys(self.locations[self.current_location_index])
                search_keywords.click()
                search_keywords.send_keys(Keys.RETURN)

                if not self.check_no_results():
                    break
                else:
                    self.log_info(f"No matching jobs found in {self.locations[self.current_location_index]}.")
                    self.current_location_index += 1

            except TimeoutException:
                self.log_info("Timeout while trying to access the Jobs page or elements on it.")
                self.current_location_index += 1
            except Exception as e:
                self.log_error(f"Job search error: {e}")
                self.current_location_index += 1

    def construct_url(self):
        """Construct the URL for job search with applied filters."""
        current_location = self.locations[self.current_location_index]
        params = {
            "keywords": f"({self.keywords}) NOT ({self.keywords_to_avoid})",
            "origin": "JOB_SEARCH_PAGE_JOB_FILTER",
            "refresh": "true",
            "sortBy": self.sort_by,
        }

        if self.filters.get("easy_apply"):
            params["f_AL"] = "true"

        if self.filters.get("experience"):
            params["f_E"] = ",".join(
                [self.EXPERIENCE_MAPPING[exp] for exp in self.filters["experience"]]
            )

        if self.filters.get("jobType"):
            params["f_JT"] = ",".join(
                [self.JOB_TYPE_MAPPING[jt] for jt in self.filters["jobType"]]
            )

        if self.filters.get("timePostedRange"):
            params["f_TPR"] = ",".join(
                [self.TIME_POSTED_MAPPING[time] for time in self.filters["timePostedRange"]]
            )

        if self.filters.get("workplaceType"):
            params["f_WT"] = ",".join(
                [self.WORKPLACE_TYPE_MAPPING[wt] for wt in self.filters["workplaceType"]]
            )

        if self.filters.get("less_than_10_applicants"):
            params["f_EA"] = "true"

        if current_location in self.LOCATION_MAPPING:
            params["geoId"] = self.LOCATION_MAPPING[current_location]

        query_string = urllib.parse.urlencode(params, safe=",")
        url = f"{self.BASE_URL}?{query_string}"
        return url

    def apply_filters_and_search(self):
        """Apply filters to the job search and navigate to the search URL."""
        while self.current_location_index < len(self.locations):
            search_url = self.construct_url()
            self.driver.get(search_url)

            if self.check_no_results():
                self.log_info(f"No matching jobs found in {self.locations[self.current_location_index]}.")
                self.current_location_index += 1
            else:
                break

    def check_no_results(self):
        """Check if the job search resulted in no matches."""
        try:
            no_results_element = self.driver.find_element(
                By.CSS_SELECTOR, "div.jobs-search-no-results-banner"
            )
            return no_results_element.is_displayed()
        except NoSuchElementException:
            return False

    def find_element_with_retry(self, by, value, retries=3, delay=2):
        """Find an element with retry logic."""
        for _ in range(retries):
            try:
                return self.driver.find_element(by, value)
            except (NoSuchElementException, StaleElementReferenceException):
                time.sleep(delay)
        raise NoSuchElementException(f"Element not found: {by}, {value}")

    def get_response_for_label(self, label_text):
        """Get user response for a given label text."""
        current_location = self.locations[self.current_location_index]
        if current_location in self.context_data["user_inputs"]:
            location_specific_inputs = self.context_data["user_inputs"][current_location]
            if label_text in location_specific_inputs:
                return location_specific_inputs[label_text]

        user_input = input(f"Please provide the answer for '{label_text}': ")
        if current_location not in self.context_data["user_inputs"]:
            self.context_data["user_inputs"][current_location] = {}
        self.context_data["user_inputs"][current_location][label_text] = user_input
        self.update_config_file()
        return user_input

    def get_checkbox_response_for_label(self, label_text):
        """Get user response for a checkbox labeled by the given text."""
        current_location = self.locations[self.current_location_index]
        if current_location in self.context_data["user_inputs"]:
            location_specific_inputs = self.context_data["user_inputs"][current_location]
            if label_text in location_specific_inputs:
                return location_specific_inputs[label_text]

        while True:
            user_input = input(f"Do you want to check the box for '{label_text}'? (yes/no): ").strip().lower()
            if user_input in ["yes", "no"]:
                response = user_input == "yes"
                if current_location not in self.context_data["user_inputs"]:
                    self.context_data["user_inputs"][current_location] = {}
                self.context_data["user_inputs"][current_location][label_text] = response
                self.update_config_file()
                return response

    def get_radio_response_for_label(self, label_text, options):
        """Get user response for a radio button group labeled by the given text."""
        current_location = self.locations[self.current_location_index]
        if current_location in self.context_data["user_inputs"]:
            location_specific_inputs = self.context_data["user_inputs"][current_location]
            if label_text in location_specific_inputs:
                return location_specific_inputs[label_text]

        while True:
            print(f"Please select an option for '{label_text}':")
            for i, option in enumerate(options):
                print(f"{i + 1}. {option}")
            user_input = input("Enter the number of your choice: ").strip()
            if user_input.isdigit() and 1 <= int(user_input) <= len(options):
                response = options[int(user_input) - 1]
                if current_location not in self.context_data["user_inputs"]:
                    self.context_data["user_inputs"][current_location] = {}
                self.context_data["user_inputs"][current_location][label_text] = response
                self.update_config_file()
                return response
            else:
                print("Invalid input, please try again.")

    def get_file_response_for_label(self, label_text):
        """Get user response for a file upload labeled by the given text."""
        current_location = self.locations[self.current_location_index]
        if current_location in self.context_data["user_inputs"]:
            location_specific_inputs = self.context_data["user_inputs"][current_location]
            if label_text in location_specific_inputs:
                return location_specific_inputs[label_text]

        user_input = input(f"Please provide the file location for '{label_text}': ")
        if current_location not in self.context_data["user_inputs"]:
            self.context_data["user_inputs"][current_location] = {}
        self.context_data["user_inputs"][current_location][label_text] = user_input
        self.update_config_file()
        return user_input

    def update_config_file(self):
        """Update the configuration file with the latest user inputs."""
        with open("config.json", "w") as config_file:
            json.dump(self.context_data, config_file, indent=4)

    def find_offers(self):
        """Find and apply to job offers."""
        while self.current_location_index < len(self.locations):
            self.apply_filters_and_search()
            
            current_page = 1

            while True:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout__list-container"))
                    )

                    job_list_container = self.find_element_with_retry(By.CLASS_NAME, "scaffold-layout__list-container")
                    job_list_items = job_list_container.find_elements(By.TAG_NAME, "li")

                    for index in range(len(job_list_items)):
                        try:
                            job_list_container = self.find_element_with_retry(By.CLASS_NAME, "scaffold-layout__list-container")
                            job_list_items = job_list_container.find_elements(By.TAG_NAME, "li")

                            if index >= len(job_list_items):
                                break

                            job_item = job_list_items[index]
                            
                            # Scroll the element into view
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", job_item)
                            time.sleep(1)
                            
                            try:
                                # Attempt to click the element with JavaScript
                                self.driver.execute_script("arguments[0].click();", job_item)
                            except ElementClickInterceptedException:
                                self.log_info("Element click intercepted, skipping to next job...")
                                continue

                            time.sleep(2)

                            WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.CLASS_NAME, "jobs-search__job-details--wrapper")
                                )
                            )

                            company_name = self.get_company_name(job_item)
                            
                            if company_name in self.applied_companies:
                                self.log_info(f"Already applied to a job at {company_name}, skipping...")
                                self.close_application_modal()
                                continue

                            job_details_wrapper = self.find_element_with_retry(By.CLASS_NAME, "jobs-search__job-details--wrapper")

                            try:
                                apply_button = job_details_wrapper.find_element(
                                    By.CSS_SELECTOR, "button.jobs-apply-button.artdeco-button--primary"
                                )
                                apply_button.click()
                                time.sleep(2)

                                WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located(
                                        (By.CSS_SELECTOR, "div.jobs-easy-apply-modal")
                                    )
                                )

                                try:
                                    self.handle_easy_apply()
                                    self.log_applied_company(company_name)
                                except Exception as e:
                                    self.log_info(f"Failed to apply at {company_name}: {str(e)}")
                                    self.log_failed_application(company_name)

                            except NoSuchElementException:
                                self.log_info("No apply button found, continuing to next job...")
                                continue

                        except (NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException) as e:
                            self.log_info(f"Exception occurred: {e}, continuing to next job...")
                            self.log_error(f"Find offers error: {e}")
                            continue

                    try:
                        pagination_container = self.find_element_with_retry(By.CLASS_NAME, "artdeco-pagination__pages")
                        next_page_button = pagination_container.find_element(
                            By.XPATH,
                            f"//button[@aria-label='Page {current_page + 1}']",
                        )
                        self.driver.execute_script("arguments[0].click();", next_page_button)
                        time.sleep(2)
                        current_page += 1
                    except NoSuchElementException:
                        self.log_info("No more pages left.")
                        break
                except TimeoutException:
                    self.log_info("Timeout while waiting for job list container.")
                    self.log_error("Timeout while waiting for job list container.")
                    break

            self.current_location_index += 1

    def get_company_name(self, job_item):
        """Extract the company name from a job listing."""
        try:
            company_element = job_item.find_element(
                By.CSS_SELECTOR,
                "div.artdeco-entity-lockup__subtitle span.job-card-container__primary-description",
            )
            return company_element.text.strip()
        except NoSuchElementException:
            return None

    def handle_easy_apply(self):
        """Handle the easy apply process."""
        while True:
            try:
                modal_dialog = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.artdeco-modal--layer-default.jobs-easy-apply-modal")
                    )
                )
                try:
                    next_button = modal_dialog.find_element(
                        By.CSS_SELECTOR, "button[data-easy-apply-next-button]"
                    )
                    self.driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(2)
                except NoSuchElementException:
                    try:
                        review_button = modal_dialog.find_element(
                            By.CSS_SELECTOR, "button[aria-label='Review your application']"
                        )
                        self.driver.execute_script("arguments[0].click();", review_button)
                        time.sleep(2)
                    except NoSuchElementException:
                        try:
                            submit_button = modal_dialog.find_element(
                                By.CSS_SELECTOR, "button[aria-label='Submit application']"
                            )
                            self.driver.execute_script("arguments[0].click();", submit_button)
                            time.sleep(2)
                            self.log_info("Application submitted.")
                            self.handle_done_button()
                            break
                        except NoSuchElementException:
                            self.log_info("Submit button not found, continuing to next job...")
                            self.close_application_modal()
                            break
                self.fill_form(modal_dialog)
            except TimeoutException:
                self.log_info("No more steps found, exiting...")
                break
            except Exception as e:
                self.log_info(f"Error during easy apply: {e}, skipping to next job...")
                self.log_error(f"Easy apply error: {e}")
                self.close_application_modal()
                break

    def fill_form(self, modal_dialog):
        """Fill out the application form."""
        form_elements = modal_dialog.find_elements(
            By.CSS_SELECTOR, "div[data-test-form-element], fieldset[data-test-form-builder-radio-button-form-component], fieldset[data-test-checkbox-form-component]"
        )
        for element in form_elements:
            try:
                label = element.find_element(By.CSS_SELECTOR, "label, legend")
                input_field = element.find_element(By.CSS_SELECTOR, "input, select, textarea")
                label_text = label.text.strip()

                if input_field.tag_name == "input" and input_field.get_attribute("type") == "text":
                    response = self.get_response_for_label(label_text)
                    if input_field.get_attribute("value") == "":
                        input_field.send_keys(response)
                        time.sleep(1)
                        input_field.send_keys(Keys.ARROW_DOWN)
                        input_field.send_keys(Keys.RETURN)

                elif input_field.tag_name == "select":
                    response = self.get_response_for_label(label_text)
                    select_options = input_field.find_elements(By.TAG_NAME, "option")
                    for option in select_options:
                        if option.get_attribute("value") == response:
                            option.click()
                            break

                elif input_field.tag_name == "textarea":
                    response = self.get_response_for_label(label_text)
                    if input_field.get_attribute("value") == "":
                        input_field.send_keys(response)

                elif input_field.tag_name == "input" and input_field.get_attribute("type") == "checkbox":
                    checkboxes = element.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                    for checkbox in checkboxes:
                        checkbox_label = checkbox.find_element(By.XPATH, "./following-sibling::label").text.strip()
                        response = self.get_checkbox_response_for_label(checkbox_label)
                        if response is not None:
                            try:
                                if response and not checkbox.is_selected():
                                    self.driver.execute_script("arguments[0].click();", checkbox)
                                elif not response and checkbox.is_selected():
                                    self.driver.execute_script("arguments[0].click();", checkbox)
                            except ElementClickInterceptedException:
                                self.driver.execute_script("arguments[0].click();", checkbox)
                            except StaleElementReferenceException:
                                checkbox = element.find_element(By.XPATH, f".//input[@type='checkbox' and ./following-sibling::label[text()='{checkbox_label}']]")
                                if response and not checkbox.is_selected():
                                    self.driver.execute_script("arguments[0].click();", checkbox)
                                elif not response and checkbox.is_selected():
                                    self.driver.execute_script("arguments[0].click();", checkbox)

                elif input_field.tag_name == "input" and input_field.get_attribute("type") == "radio":
                    radio_buttons = element.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    for radio in radio_buttons:
                        radio_label = radio.find_element(By.XPATH, "./following-sibling::label").text.strip()
                        response = self.get_radio_response_for_label(label_text, [rb.find_element(By.XPATH, "./following-sibling::label").text.strip() for rb in radio_buttons])
                        if response.lower() == radio_label.lower():
                            try:
                                radio.click()
                            except ElementClickInterceptedException:
                                self.driver.execute_script("arguments[0].click();", radio)
                            break

                elif input_field.tag_name == "input" and input_field.get_attribute("type") == "file":
                    response = self.get_file_response_for_label(label_text)
                    input_field.send_keys(response)
                    time.sleep(1)

            except NoSuchElementException:
                continue

        try:
            next_button = modal_dialog.find_element(By.CSS_SELECTOR, "button[data-easy-apply-next-button]")
            next_button.click()
            time.sleep(2)
        except NoSuchElementException:
            self.log_info("Next button not found, form might be complete or there is an issue.")

    def handle_done_button(self):
        """Handle the final done button after application submission."""
        try:
            done_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.artdeco-button.artdeco-button--primary"))
            )
            done_button.click()
            time.sleep(2)
        except TimeoutException:
            self.log_info("Done button not found, skipping to next job.")

    def close_application_modal(self):
        """Close the application modal."""
        try:
            close_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "button.artdeco-button.artdeco-button--circle.artdeco-button--muted.artdeco-button--2.artdeco-button--tertiary.artdeco-modal__dismiss",
                    )
                )
            )
            close_button.click()
            time.sleep(2)
            self.handle_discard_dialog()
        except TimeoutException:
            self.log_info("Close button not found, skipping to next job.")

    def handle_discard_dialog(self):
        """Handle the discard dialog when closing the application modal."""
        try:
            discard_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "button[data-control-name='discard_application_confirm_btn']")
                )
            )
            discard_button.click()
            time.sleep(2)
        except TimeoutException:
            self.log_info("Discard button not found, skipping to next job.")

    def close_session(self):
        """Close the browser session."""
        self.log_info("End of the session")
        self.driver.close()
        self.driver.quit()

    def handle_captcha(self):
        """Handle CAPTCHA prompts manually."""
        input("CAPTCHA detected. Please solve the CAPTCHA manually and then press Enter to continue...")


if __name__ == "__main__":
    with open("config.json") as config_file:
        data = json.load(config_file)
    bot = EasyApplyLinkedin(data)
    bot.login_linkedin()
    bot.job_search()
    bot.find_offers()
    bot.close_session()
