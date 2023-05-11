from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.expected_conditions import invisibility_of_element_located
import time
import random
import threading
from queue import Queue
from selenium.common.exceptions import NoSuchElementException
import nltk


max_simultaneous_profiles = 3
metamask_url = f"chrome-extension://cfkgdnlcieooajdnoehjhgbmpbiacopjflbjpnkm/home.html#"
chrome_driver_path = Service("C:\\Soft\\Myshit\\chromedriver111\\chromedriver\\chromedriver-win-x64.exe")



start_idx = int(input("Enter the starting index of the profile range: "))
end_idx = int(input("Enter the ending index of the profile range: "))

with open("config\\profile_ids.txt", "r") as file:
    profile_ids = [line.strip() for line in file.readlines()]
with open("config\\passwords.txt", "r") as file:
    passwords = [line.strip() for line in file.readlines()]
nltk.download('words')
english_words = nltk.corpus.words.words()
holograph_url = f'https://app.holograph.xyz'
def input_text_if_exists(driver, locator, text, by=By.XPATH, timeout=20):
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
            element.send_keys(text)
            return True
        except TimeoutException:
            return False
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(3)
    return False
def click_if_exists(driver, locator, by=By.XPATH):
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((by, locator))
            )
            WebDriverWait(driver, 10).until(
                invisibility_of_element_located((By.CSS_SELECTOR, ".loading-overlay"))
            )

            element.click()
            return True
        except TimeoutException:
            return False
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(3)
    return False
def worker():
    while True:
        idx, profile_id = task_queue.get()
        if profile_id is None:
            break
        process_profile(idx, profile_id)
        task_queue.task_done()
def upload_image(driver, file_input_xpath, image_file_path):
    # Make the file input visible
    driver.execute_script('''
    var element = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    element.style.display = "block";
    element.style.visibility = "visible";
    ''', file_input_xpath)

    # Now upload the image
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, file_input_xpath)))
    file_input = driver.find_element(By.XPATH, file_input_xpath)
    file_input.send_keys(image_file_path)
def generate_random_word():
    while True:
        random_word = random.choice(english_words)
        if len(random_word) == 10:
            return random_word
def fill_in_fields(driver, name_field_xpath, symbol_field_xpath, description_field_xpath=None):
    collection_name = generate_random_word()
    collection_symbol = collection_name[:3].upper()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, name_field_xpath)))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, symbol_field_xpath)))

    name_field = driver.find_element(By.XPATH, name_field_xpath)
    symbol_field = driver.find_element(By.XPATH, symbol_field_xpath)

    name_field.send_keys(collection_name)
    symbol_field.send_keys(collection_symbol)

    if description_field_xpath is not None:
        sentence = ' '.join(random.sample(nltk.corpus.words.words(), 4))  # Adjust this to your needs
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, description_field_xpath)))
        description_field = driver.find_element(By.XPATH, description_field_xpath)
        description_field.send_keys(sentence)
def element_exists(driver, xpath):
    time.sleep(random.uniform(1.2, 1.7))
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        return True
    except NoSuchElementException:
        return False
def confirm_connection(driver):
    metamask_window_handle = None
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if 'MetaMask Notification' in driver.title:
            metamask_window_handle = handle
            break
    if metamask_window_handle:
        Confirm_conection_xpath = '/html/body/div[1]/div/div[2]/div/div[3]/div[2]/button[2]'
        Confirm_conection2_xpath = '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/footer/button[2]'
        Confirm_conection3_xpath = '/html/body/div[1]/div/div[2]/div/div[3]/button[2]'

        button_clicked = click_if_exists(driver, Confirm_conection_xpath)
        if button_clicked:
            click_if_exists(driver, Confirm_conection2_xpath)
            click_if_exists(driver, Confirm_conection3_xpath)
        else:
            click_if_exists(driver, Confirm_conection3_xpath)

        print("Metamask is connected")
    else:
        print("MetaMask already connected")
    driver.switch_to.window(driver.window_handles[0])
def process_profile(idx, profile_id):

    print(f"Opening ID {idx}: {profile_id}")
    req_url = f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1'
    response = requests.get(req_url)
    response_json = response.json()
    print(response_json)
    port = str(response_json['automation']['port'])
    options = webdriver.ChromeOptions()
    options.debugger_address = f'127.0.0.1:{port}'
    driver = webdriver.Chrome(service=chrome_driver_path, options=options)
    initial_window_handle = driver.current_window_handle

    driver.get(metamask_url)
    try:
        for tab in driver.window_handles:
            if tab != initial_window_handle:
                driver.switch_to.window(tab)
                driver.close()
        driver.switch_to.window(initial_window_handle)
        password_input = '//*[@id="password"]'
        input_text_if_exists(driver, password_input, passwords[idx - 1])
        click_if_exists(driver, '//*[@id="app-content"]/div/div[3]/div/div/button')
        click_if_exists(driver, '/html/body/div[1]/div/div[1]/div/div[2]/div/div')
        time.sleep(random.uniform(1.2, 1.3))
        click_if_exists(driver, "//*[contains(text(), 'Ethereum Mainnet')]")
        time.sleep(random.uniform(0.7, 1.3))
        driver.get(holograph_url)
        click_if_exists(driver, '/html/body/div/main/header/nav/div/div[2]/div/div/div/div[1]/span')
        time.sleep(random.uniform(0.7, 1.3))
        click_if_exists(driver, '/html/body/div/aside[1]/div/div/div/span[2]')
        time.sleep(random.uniform(1.7, 2.6))
        confirm_connection(driver)
        time.sleep(random.uniform(0.7, 1.3))
        click_if_exists(driver, '/html/body/div/main/header/nav/div/div[3]/div/div[2]/div[1]/div')
        time.sleep(random.uniform(0.7, 1.3))
        click_if_exists(driver, '/html/body/div/main/header/nav/div/div[3]/div/div[2]/div[2]/div/button/div/span[1]')
        time.sleep(random.uniform(0.7, 1.3))
        click_if_exists(driver, '/html/body/div/main/div[2]/button')
        time.sleep(random.uniform(0.7, 1.3))
        fill_in_fields(driver, "/html/body/div/main/main/div/form/div[1]/div/input",
                       "/html/body/div/main/main/div/form/div[2]/div/input")
        time.sleep(random.uniform(0.7, 1.3))
        click_if_exists(driver, '/html/body/div/main/main/div/form/div[5]/button')
        time.sleep(random.uniform(0.7, 1.3))
        click_if_exists(driver, '/html/body/div/main/div[2]/button')
        time.sleep(random.uniform(0.7, 1.3))
        fill_in_fields(driver, "/html/body/div/main/main/div/form/div[1]/div[2]/div[1]/div/input",
                       "/html/body/div/main/main/div/form/div[1]/div[2]/div[2]/div/input",
                       "/html/body/div/main/main/div/form/div[1]/div[2]/div[3]/div/textarea")
        image_file_path = f"image\\image ({idx}).jpg"
        file_input_xpath = '/html/body/div/main/main/div/form/div[1]/input'
        upload_image(driver, file_input_xpath, image_file_path)
        click_if_exists(driver, '/html/body/div/main/main/div/form/div[2]/button[2]')
        time.sleep(3)
        driver.close()
        print(f"Done for profile №{idx}!")
    except Exception as e:
        print(f"Fail for profile №{idx} erorr - {e}!")
        driver.quit()

task_queue = Queue(max_simultaneous_profiles)
threads = []

for _ in range(max_simultaneous_profiles):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

for idx, profile_id in zip(range(start_idx, end_idx + 1), profile_ids[start_idx - 1:end_idx]):
    task_queue.put((idx, profile_id))
    time.sleep(20)

task_queue.join()

for _ in range(max_simultaneous_profiles):
    task_queue.put((None, None))

for t in threads:
    t.join()
#PERFORM BY @BROKEBOI_CAPITAL & GPT4