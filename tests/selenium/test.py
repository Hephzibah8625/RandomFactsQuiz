import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time

# Configuration or constants for easy management
APP_URL = "http://localhost:8501"
USERNAME_INPUT_CSS = "input[aria-label='Username']"
PASSWORD_INPUT_CSS = "input[aria-label='Password']"
NEW_USERNAME_INPUT_CSS = "input[aria-label='New Username']"
NEW_PASSWORD_INPUT_CSS = "input[aria-label='New Password']"
QUESTION_NUMBER_INPUT_CSS = "input[aria-label='Number of Questions:']"
LOGIN_BUTTON_XPATH = "//button[contains(., 'Login')]"
LOGOUT_BUTTON_XPATH = "//button[contains(., 'Logout')]"
REGISTER_BUTTON_XPATH = "//button[contains(., 'Register')]"
RADIO_INPUT_XPATH = "//input[@type='radio']"
START_QUIZ_BUTTON_XPATH = "//button[contains(., 'Start Quiz')]"
PLAY_AGAIN_BUTTON_XPATH = "//button[contains(., 'Play Again')]"


class StreamlitAppTestCase(unittest.TestCase):
    """Streamlit application Selenium test cases."""
    
    def setUp(self):
        service = Service("/usr/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service)
        self.driver.get(APP_URL)

    def click_dropdown_menu_option(self, option_text):
        menu_button = self.driver.find_element(By.XPATH, f"//div[contains(text(), '{option_text}')]")
        menu_button.click()

    def fill_form_field(self, field_css, text):
        input_field = self.driver.find_element(By.CSS_SELECTOR, field_css)
        input_field.send_keys(text)

    def test_1_registration(self):
        """Tests the registration process of a new user."""
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, LOGIN_BUTTON_XPATH))
        )
        self.click_dropdown_menu_option('Sign In')

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-baseweb='popover']//div[contains(text(), 'Sign Up')]"))
        ).click()

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, NEW_USERNAME_INPUT_CSS))
        )
        self.fill_form_field(NEW_USERNAME_INPUT_CSS, "test")
        self.fill_form_field(NEW_PASSWORD_INPUT_CSS, "test")

        register_button = self.driver.find_element(By.XPATH, REGISTER_BUTTON_XPATH)
        register_button.click()

    def test_2_login_and_play(self):
        """Tests the login and play functionality."""
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, USERNAME_INPUT_CSS))
        )

        self.fill_form_field(USERNAME_INPUT_CSS, "test")
        self.fill_form_field(PASSWORD_INPUT_CSS, "test")

        login_button = self.driver.find_element(By.XPATH, LOGIN_BUTTON_XPATH)
        login_button.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, LOGOUT_BUTTON_XPATH))
        )

        questions_num = self.driver.find_element(By.CSS_SELECTOR, QUESTION_NUMBER_INPUT_CSS)
        start_button = self.driver.find_element(By.XPATH, START_QUIZ_BUTTON_XPATH)
        questions_num.send_keys(Keys.CONTROL + "a")        
        questions_num.send_keys(Keys.BACK_SPACE)
        questions_num.send_keys("6")
        start_button.click()

        # Wait until the radio buttons are loaded
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, RADIO_INPUT_XPATH))
        )

        radio_buttons = self.driver.find_elements(By.XPATH, RADIO_INPUT_XPATH)
        for i in range(0, len(radio_buttons), 2):  # Assuming there are two options per question
            # Get the parent element, which is assumed to be immediately above the radio button in the DOM
            parent_element = radio_buttons[i].find_element(By.XPATH, "./..")
            
            # Click the parent element
            parent_element.click()
            time.sleep(1)
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, PLAY_AGAIN_BUTTON_XPATH))
        )
        
        play_button = self.driver.find_element(By.XPATH, PLAY_AGAIN_BUTTON_XPATH)
        play_button.click()

        time.sleep(1)

        logout_button = self.driver.find_element(By.XPATH, LOGOUT_BUTTON_XPATH)
        logout_button.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, LOGIN_BUTTON_XPATH))
        )
        time.sleep(1)

    def tearDown(self):
        """Tears down the test environment."""
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
