# Download the chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads and put it in the current directory
# Pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# Put the identification json from Google in keys/API_identification.json

from __future__ import print_function
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import numpy as np
import os, time, math, pickle
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

waiting_time = 1.5

def connect_to_facebook(driver):
    # Opening Facebook
    driver.get("https://www.facebook.com")
    time.sleep(waiting_time)
    print("Opened facebook")
    user = input('Enter your Facebook email: ')
    pwd = input('Enter your Facebook password: ')

    # Logging in
    username_box = driver.find_element_by_id('email')
    username_box.send_keys(user)
    password_box = driver.find_element_by_id('pass')
    password_box.send_keys(pwd)
    login_box = driver.find_element_by_id('loginbutton')
    time.sleep(waiting_time/2)
    login_box.click()
    time.sleep(waiting_time)
    print("Logged in")


def open_friends_page(driver):
    # Go to your profile
    driver.get("https://www.facebook.com/profile")
    time.sleep(waiting_time)
    # Click on the friend's page
    friends = driver.find_element_by_xpath("//*[@data-tab-key='friends']")
    friends.click()
    time.sleep(1)


def get_number_friends(driver):
    # Go to your profile
    driver.get("https://www.facebook.com/profile")
    time.sleep(waiting_time)
    # Click on the friend's page
    try:
        friends = driver.find_element_by_xpath("//*[@data-tab-key='friends']")
    except NoSuchElementException:
        driver.get("https://www.facebook.com/profile")
        time.sleep(waiting_time*2)
        friends = driver.find_element_by_xpath("//*[@data-tab-key='friends']")
    friends.click()
    time.sleep(waiting_time)
    # Find your number of friends
    nbr_friends = driver.find_element_by_xpath("//*[@class='_gs6']")
    all_friends = int(nbr_friends.text)
    return(all_friends)


def scroll_down(driver, nbr_times):
    i = 1
    while i <= nbr_times:
        # Scroll down
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight || document.documentElement.scrollHeight)")
        time.sleep(waiting_time/2)
        i += 1


def open_friend_profile(driver, friend_number):
    # Scroll down and click on the friend
    scroll_down(driver, math.floor(friend_number / 8) + 1)
    try:
        all_friends = driver.find_elements_by_xpath("//*[@class='fsl fwb fcb']")
        friend = all_friends[friend_number]
        actions = ActionChains(driver)
        actions.move_to_element(friend).click().perform()

    # In case of error we reopen the friends page to access the profile
    except NoSuchElementException:
        open_friends_page(driver)
        time.sleep(waiting_time)
        scroll_down(driver, math.floor(friend_number / 8) + 1)
        all_friends = driver.find_elements_by_xpath("//*[@class='fsl fwb fcb']")
        friend = all_friends[friend_number]
        actions = ActionChains(driver)
        actions.move_to_element(friend).click().perform()
    except ElementClickInterceptedException:
        open_friends_page(driver)
        time.sleep(waiting_time)
        scroll_down(driver, math.floor(friend_number / 8) + 1)
        all_friends = driver.find_elements_by_xpath("//*[@class='fsl fwb fcb']")
        friend = all_friends[friend_number]
        actions = ActionChains(driver)
        actions.move_to_element(friend).click().perform()
    except IndexError:
        open_friends_page(driver)
        time.sleep(waiting_time)
        scroll_down(driver, math.floor(friend_number / 8) + 1)
        all_friends = driver.find_elements_by_xpath("//*[@class='fsl fwb fcb']")
        friend = all_friends[friend_number]
        actions = ActionChains(driver)
        actions.move_to_element(friend).click().perform()
    except Exception:
        open_friends_page(driver)
        time.sleep(waiting_time)
        scroll_down(driver, math.floor(friend_number / 8) + 1)
        all_friends = driver.find_elements_by_xpath("//*[@class='fsl fwb fcb']")
        friend = all_friends[friend_number]
        actions = ActionChains(driver)
        actions.move_to_element(friend).click().perform()
    time.sleep(waiting_time)


def get_birthday_of_friend(driver, friend_number, list_friends):
    open_friend_profile(driver, friend_number)
    # Click on the 'about' page on the friend's page
    try:
        about = driver.find_element_by_xpath("//*[@data-tab-key='about']")
        actions = ActionChains(driver)
        actions.move_to_element(about).perform()
    except NoSuchElementException:
        open_friends_page(driver)
        open_friend_profile(driver, friend_number)
        time.sleep(waiting_time)
        try:
            about = driver.find_element_by_xpath("//*[@data-tab-key='about']")
            actions = ActionChains(driver)
            actions.move_to_element(about).perform()
        except Exception:
            pass
    try:
        about.click()
    except ElementClickInterceptedException:
        # We try to reopen the friend's page
        open_friends_page(driver)
        open_friend_profile(driver, friend_number)
        time.sleep(waiting_time)
        about = driver.find_element_by_xpath("//*[@data-tab-key='about']")
        actions = ActionChains(driver)
        actions.move_to_element(about).perform()
        try:
            about.click()
        except Exception:
            pass
    time.sleep(waiting_time)

    # Get the birthday
    try:
        birthday = driver.find_elements_by_xpath("(//*[contains(text(), 'Birthday')])[1]/parent::*/following-sibling::*")
        birthday_friend = birthday[0].text
    except IndexError:
        birthday_friend = ''
    friend = driver.find_element_by_xpath("//*[@class='_2nlw _2nlv']")
    name_friend = friend.text

    # Go back two pages
    driver.back()
    driver.back()
    time.sleep(waiting_time)
    the_list = list_friends.append({'Name': name_friend, 'Birthday': birthday_friend}, ignore_index=True)
    return the_list


def convert_to_date(the_date):
    # Trying the two possible formats
    try:
        birthday = datetime.strptime(the_date, '%B %d, %Y')
    except ValueError:
        try:
            birthday = datetime.strptime(the_date, '%B %d')
        except Exception:
            birthday = ''
    except Exception:
        birthday = ''
    return birthday


def set_up_google_calendar():
    creds = None
    address = ['https://www.googleapis.com/auth/calendar']

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'keys/API_identification.json', address)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service


def create_gcal_event(service, your_email, birthday, name):
    name_cal = 'Birthday - ' + name
    event = {
        'summary': name_cal,
        'start': {
            'date': str(birthday)[:10],
            'timeZone': 'America/New_York'
        },
        'end': {
            'date': str(birthday)[:10],
            'timeZone': 'America/New_York'
        },
        'recurrence': [
            'RRULE:FREQ=YEARLY',
        ],
        'attendees': [
            {
                'email': your_email,
            },
        ],
    }
    recurring_event = service.events().insert(calendarId='primary', body=event).execute()


def run():
    # Setting up Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    # chrome_options.add_argument("--headless")
    chrome_driver = os.getcwd() +"\\chromedriver.exe"
    driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
    # Asking for the number of friends
    list_friends = pd.DataFrame(columns=['Name', 'Birthday'])
    friends_nbr_wanted = 0
    while friends_nbr_wanted == 0:
        friends_nbr_wanted = input('Of how many friends do you want the birthday? ')
        try:
            friends_nbr_wanted = int(friends_nbr_wanted)
            if friends_nbr_wanted <= 0:
                raise ValueError()
        except ValueError:
            print("Enter a number >0")
            friends_nbr_wanted = 0
        except Exception:
            print("Enter a number >0")
            friends_nbr_wanted = 0
    # Getting friend's birthdays
    connect_to_facebook(driver)
    count_friends = get_number_friends(driver)
    open_friends_page(driver)
    print("On Friend's page")
    i = 1
    while i <= min(count_friends, friends_nbr_wanted):
        print("Processing info for friend #" + str(i))
        list_friends = get_birthday_of_friend(driver, i-1, list_friends)
        i += 1
    # Transform date
    list_friends['Birthday'] = list_friends['Birthday'].apply(convert_to_date)
    print(list_friends)
    # Also Writing in a csv
    list_friends.to_csv("birthday.csv", index=False)
    print("All birthdays collected")
    your_email = input("Enter your Gmail address used for your calendar: ")
    # We just put all dates to 2019
    list_friends["Birthday"] = list_friends["Birthday"].apply(lambda x: x.replace(year=2019))
    # Setting up Google calendar
    the_service = set_up_google_calendar()
    print("Creating Google Calendar events")
    # Creating the Google calendar event for each friend, if we have a birthday
    i = 1
    while i <= len(list_friends):
        try:
            create_gcal_event(the_service, your_email, list_friends["Birthday"][i-1], list_friends["Name"][i-1])
            print("Event created for " + str(list_friends["Name"][i-1]))
        except ValueError:
            pass
        except Exception:
            pass
        i += 1
    print("All Google Calendar events created")
    print("Done.")


if __name__ == '__main__':
    run()