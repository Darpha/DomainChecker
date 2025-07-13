import os
from os.path import expanduser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep

import os
import sys


# Determine if the application is frozen to extract chromedriver correctly
if getattr(sys, 'frozen', False):
    # The application is frozen
    driver_path = os.path.join(sys._MEIPASS, 'chromedriver.exe')
else:
    # The application is not frozen
    driver_path = 'chromedriver.exe'


# Clear screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_ascii_art():
    ascii_art = """
    ____                        _          ________              __                _    _____
   / __ \____  ____ ___  ____ _(_____     / ____/ /_  ___  _____/ /_____  _____   | |  / <  /
  / / / / __ \/ __ `__ \/ __ `/ / __ \   / /   / __ \/ _ \/ ___/ //_/ _ \/ ___/   | | / // / 
 / /_/ / /_/ / / / / / / /_/ / / / / /  / /___/ / / /  __/ /__/ ,< /  __/ /       | |/ // /  
/_____/\____/_/ /_/ /_/\__,_/_/_/ /_/   \____/_/ /_/\___/\___/_/|_|\___/_/        |___//_/                                                                                                                                                                                                                        
"""
    print(ascii_art)

# Store status messages 
status_messages = []
all_domains = [] 

# Print available and unavailable domains
def print_status(domain, available):
    color = "\033[92m" if available else "\033[91m"  # Green for available, red for unavailable
    status = f"{domain}.no: {color}{'Available' if available else 'Unavailable'}\033[0m"
    all_domains.append((domain, available))  # Add to all_domains list
    if len(status_messages) >= 6:  # Keep only the last 6 status messages
        status_messages.pop(0)  # Remove the oldest (first) status message
    status_messages.append(status)

# Function to write available domains to a text file
def save_available_domains():
    home = expanduser("~")
    desktop_path = os.path.join(home, "Desktop")
    results_path = os.path.join(desktop_path, "results.txt")
    with open(results_path, 'w') as file:
        for domain, available in all_domains:
            if available:
                file.write(f"{domain}.no\n")

def print_output(scan_done=False):
    clear_screen()
    print_ascii_art()
    print("\nDomain status:")
    for message in status_messages:  # Directly print each message
        print(message)
    if scan_done:
        print("\nAvailable domains:")
        for domain, available in all_domains:
            if available:  # Print only available domains and in green
                print(f"{domain}.no \033[92mAvailable\033[0m")

# Function to get file path for "domains check.txt" on desktop
def get_file_path():
    home = expanduser("~")
    desktop_path = os.path.join(home, "Desktop")
    file_path = os.path.join(desktop_path, "dcheck.txt")
    return file_path

# Paths
driver_path = 'chromedriver.exe'
url = 'https://www.norid.no/en/'

# Selenium setup with headless option and logging disabled
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensures Chrome runs in headless mode
chrome_options.add_argument("--log-level=3")  # Disables logging
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10)

# Get file path for "domains dcheck.txt" on desktop
file_path = get_file_path()

# Reading domains from file if exists
if os.path.exists(file_path):
    with open(file_path, 'r') as file:
        domains = file.readlines()

    # Checking domains
    for domain in domains:
        domain = domain.strip()
        driver.get(url)
        try:
            # Wait for the search box to be clickable and then type in the domain
            search_box = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'nrd-ds__search__input')))
            search_box.clear()
            search_box.send_keys(domain)
            search_box.send_keys(Keys.RETURN)

            # Wait for the result to appear
            result_header = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'nrd-ds__result__header')))

            # Check if the domain is available
            if "The domain name is available – find a registrar" in result_header.text:
                print_status(domain, True)
            else:
                print_status(domain, False)
        except Exception as e:
            print_status(domain, False)  # In case of error, mark as unavailable
        print_output()  # Update the output after each domain check

    # Final output with "Scan Done"
    print_output(scan_done=True)
    # Save available domains to a file
    save_available_domains()
else:
    print("File 'dcheck.txt' not found on desktop.")

# Close the browser
driver.quit()

# Keep the cmd open after scanning is done
print("\nScanning is complete. Press Enter to exit...")
input()  # Waits for user input before closing