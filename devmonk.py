from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
import time

# File containing XSS payloads
PAYLOAD_FILE = "xss_payloads.txt"
SUCCESS_FILE = "successful_payloads.txt"

def load_payloads(file):
    """Load XSS payloads from a file."""
    with open(file, 'r') as f:
        return [line.strip() for line in f.readlines()]

def log_success(payload):
    """Log successful payloads."""
    with open(SUCCESS_FILE, 'a') as f:
        f.write(payload + '\n')

def wait_for_login(driver):
    """Detect login page and wait for manual login."""
    print("Detecting login fields...")
    while True:
        login_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[type='password']")
        if login_fields:
            print("Login form detected. Please log in manually.")
            input("Press Enter after logging in to continue...")
            return
        time.sleep(1)

def wait_for_user_target(driver):
    """Wait for the user to interact with an input field and capture it."""
    print("Please click on or type in the target input field within the browser.")
    target_element = None

    while not target_element:
        try:
            # Continuously check the active element
            active_element = driver.switch_to.active_element
            tag_name = active_element.tag_name
            input_type = active_element.get_attribute("type")

            # Identify valid target fields
            if tag_name in ['input', 'textarea'] and input_type not in ['email', 'password']:
                print(f"Target field detected: {tag_name} (type: {input_type})")
                target_element = active_element
                break

            # If still undetected, prompt the user
            print("No valid target field detected yet. Please click and type in the desired field.")
            time.sleep(2)
        except Exception as e:
            print(f"Error detecting active element: {e}")
            time.sleep(2)

    return target_element

def inject_payloads(driver, target_element, payloads):
    """Inject payloads into the captured field and test for XSS."""
    for payload in payloads:
        try:
            # Inject payload into the target field
            target_element.clear()
            target_element.send_keys(payload)

            # Submit the form (try Enter key or find a submit button)
            target_element.send_keys(Keys.RETURN)
            time.sleep(2)  # Wait for the page to update

            # Check for XSS execution (Alert check)
            alert_triggered = False
            try:
                alert = Alert(driver)
                print(f"Success! Payload: {payload}")
                log_success(payload)
                alert.dismiss()
                alert_triggered = True  # Set flag to True if alert is triggered
            except:
                print(f"No alert for payload: {payload}")

            # Optionally: Check if the payload is reflected in the page or URL
            if not alert_triggered:
                if payload in driver.current_url or payload in driver.page_source:
                    print(f"Payload reflected in URL/page source: {payload}")
                    log_success(payload)
                    alert_triggered = True  # Set flag to True if payload is reflected

            # Ask to proceed only if the payload was successful (alert triggered or reflection)
            if alert_triggered:
                proceed = input("Proceed with next payload? (y/n): ")
                if proceed.lower() != 'y':
                    return

        except Exception as e:
            print(f"Error testing payload: {payload} - {e}")

def main():
    # Prompt for the target URL
    target_url = input("Enter the target URL (e.g., https://example.com): ")

    # Ask if the user wants to check for login fields
    check_login = input("Do you want to check for login fields? (y/n): ")

    # Initialize the browser (using Firefox)
    driver = webdriver.Firefox()

    try:
        payloads = load_payloads(PAYLOAD_FILE)

        # Open the target URL
        driver.get(target_url)
        time.sleep(2)  # Wait for the page to load

        # Check if login is required based on user input
        if check_login.lower() == 'y':
            wait_for_login(driver)

        # Wait for user to target an input field
        target_element = wait_for_user_target(driver)

        # Inject payloads into the captured field
        inject_payloads(driver, target_element, payloads)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()


