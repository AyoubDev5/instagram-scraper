import json
import random
from src.instadm import InstaDM
import os
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager as CM
from getpass import getpass
import json
import sys



ELEMENTS_TIMEOUT = 15
FOLLOW_DATA_LOADING_TIMEOUT = 50

def scrape():

    # f = open('accounts.json')
    # accounts = json.load(f)
    # for account in accounts:

    username = "your username"
    password = "your password"

    options = webdriver.ChromeOptions()
    # TODO: invoking in headless removes need for GUI
    # options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument("--lang=en")
    options.add_argument("--log-level=3")
    options.add_experimental_option("detach", True)

    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/535.19"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(executable_path=CM().install(), options=options)
    bot.set_window_size(600, 1000)

    bot.get('https://www.instagram.com/')

    time.sleep(5)

    print("Logging in...")


    user_element = WebDriverWait(bot, ELEMENTS_TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input')))


    user_element.send_keys(username)

    pass_element = WebDriverWait(bot, ELEMENTS_TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input')))

    pass_element.send_keys(password)

    login_button = WebDriverWait(bot, ELEMENTS_TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="loginForm"]/div/div[3]/button')))

    time.sleep(0.4)


    login_button.click()

    bot.get('https://www.instagram.com/{}/'.format(username))

    time.sleep(5)

    target_followers=int(500)

    # getting followers
    if target_followers > 0:
        bot.get('https://www.instagram.com/{}/'.format(username).'/followers/')

        time.sleep(5)

        ActionChains(bot).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
        ActionChains(bot).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()

    print('Scraping followers...')

    followers = set()

    not_loading_count = 0
    prev = 0
    while len(followers) < target_followers:

        ActionChains(bot).send_keys(Keys.END).perform()

        time.sleep(5)

        more_followers = bot.find_elements(By.XPATH, '//*/div[@role="button"]/a')

        followers.update(more_followers)

        #print(len(followers))
        if len(followers) == prev:
            not_loading_count += 1
        else:
            not_loading_count = 0
        if not_loading_count == FOLLOW_DATA_LOADING_TIMEOUT:
            break
        prev = len(followers)

    users_followers = set()
    c = 0
    for i in followers:
        if i.get_attribute('href'):
            c += 1
            follower = i.get_attribute('href').split("/")[3]
            print(i.get_attribute('href'))
            users_followers.add(follower)
            #print (c, ' ', follower)
        else:
            continue

    print('Saving to file...')
    print('[DONE] - Your followers are saved in followers.txt file')

    with open('infos/followers.txt', 'w') as file:
        file.write('\n'.join(users_followers) + "\n")

    print('Exiting...')

    # f = open('infos/accounts.json',)
    # accounts = json.load(f)

    with open('infos/followers.txt', 'r') as f:
        usernames = [line.strip() for line in f]

    while True:
        if not usernames:
            print('Finished usernames.')
            break

        dm_num = int(500)


        if not usernames:
            break
        # Auto login
        insta = InstaDM(username=username,
                        password=password, headless=False)

        for i in range(dm_num):

            if not usernames:
                break

            username = usernames.pop()
            # Send message
            insta.sendMessage(
                user=username, message="")

        insta.teardown()

if __name__ == '__main__':
    scrape()
