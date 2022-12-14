"""
Alright is unofficial Python wrapper for whatsapp web made as an inspiration from PyWhatsApp
allowing you to send messages, images, video and documents programmatically using Python
"""

import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    NoSuchElementException,
)
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote


# LOGGER = logging.getLogger()

class WhatsApp(object):
    def __init__(self, browser=None, time_out=600):
        # CJM - 20220419: Added time_out=600 to allow the call with less than 600 sec timeout
        # web.open(f"https://web.whatsapp.com/send?phone={phone_no}&text={quote(message)}")

        self.BASE_URL = "https://web.whatsapp.com/"
        self.suffix_link = "https://wa.me/"

        if not browser:
            browser = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=self.chrome_options,
            )

        self.browser = browser
        # CJM - 20220419: Added time_out=600 to allow the call with less than 600 sec timeout
        self.wait = WebDriverWait(self.browser, time_out)
        self.cli()
        self.login()
        self.mobile = ""

    @property
    def chrome_options(self):
        chrome_options = Options()
        if sys.platform == "win32":
            chrome_options.add_argument("--profile-directory=Default")
            chrome_options.add_argument("--user-data-dir=C:/Temp/ChromeProfile")
        else:
            chrome_options.add_argument("start-maximized")
            chrome_options.add_argument("--user-data-dir=./User_Data")
        # chrome_options.add_argument("--incognito")
        # chrome_options.headless=True
        return chrome_options

    def cli(self):
        """
        LOGGER settings  [nCKbr]
        """
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s -- [%(levelname)s] >> %(message)s")
        )
        # LOGGER.addHandler(handler)
        # LOGGER.setLevel(logging.INFO)

    def login(self):
        self.browser.get(self.BASE_URL)
        self.browser.maximize_window()

    def logout(self):
        prefix = "//div[@id='side']/header/div[2]/div/span/div[3]"
        dots_button = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"{prefix}/div[@role='button']",
                )
            )
        )
        dots_button.click()

        logout_item = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"{prefix}/span/div[1]/ul/li[last()]/div[@role='button']",
                )
            )
        )
        logout_item.click()

    def get_phone_link(self, mobile) -> str:
        """get_phone_link (), create a link based on whatsapp (wa.me) api

        Args:
            mobile ([type]): [description]

        Returns:
            str: [description]
        """
        return f"{self.suffix_link}{mobile}"

    def catch_alert(self, seconds=2):
        """catch_alert()

        catches any sudden alert
        """
        try:
            WebDriverWait(self.browser, seconds).until(EC.alert_is_present())
            alert = self.browser.switch_to_alert.accept()
            return True
        except Exception as e:
            # LOGGER.exception(f"An exception occurred: {e}")
            return False

    def find_user(self, mobile) -> None:
        """find_user()
        Makes a user with a given mobile a current target for the wrapper

        Args:
            mobile ([type]): [description]
        """
        try:
            self.mobile = mobile
            link = self.get_phone_link(mobile)
            self.browser.get(link)
            action_button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="action-button"]'))
            )
            action_button.click()
            time.sleep(2)

            # go_to_web = EC.presence_of_element_located(By.XPATH, '//*[@id="fallback_block"]/div/div/a')

            '''
            go_to_web = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="fallback_block"]/div/div/a')
                )
            )

            go_to_web.click()
            time.sleep(1)
            '''

        except UnexpectedAlertPresentException as bug:
            # LOGGER.exception(f"An exception occurred: {bug}")
            time.sleep(1)
            self.find_user(mobile)

    def find_by_username(self, username):
        """find_user_by_name ()

        locate existing contact by username or number

        Args:
            username ([type]): [description]
        """
        try:
            search_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]')
                )
            )
            search_box.clear()
            search_box.send_keys(username)
            search_box.send_keys(Keys.ENTER)
        except Exception as bug:
            garbage_val = 0
            # LOGGER.exception(f"Exception raised while finding user {username}\n{bug}")

    def username_exists(self, username):
        """username_exists ()

        Returns True or False whether the contact exists or not, and selects the contact if it exists, by checking if the search performed actually opens a conversation with that contact

        Args:
            username ([type]): [description]
        """
        try:
            search_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="side"]/div[1]/div/label/div/div[2]')
                )
            )
            search_box.clear()
            search_box.send_keys(username)
            search_box.send_keys(Keys.ENTER)
            opened_chat = self.browser.find_element_by_xpath(
                "/html/body/div/div[1]/div[1]/div[4]/div[1]/header/div[2]/div[1]/div/span"
            )
            title = opened_chat.get_attribute("title")
            if title.upper() == username.upper():
                return True
            else:
                return False
        except Exception as bug:
            garbage_val = 0
            # LOGGER.exception(f"Exception raised while finding user {username}\n{bug}")

    def get_first_chat(self, ignore_pinned=True):
        """get_first_chat()  [nCKbr]

        gets the first chat on the list of chats

        Args:
            ignore_pinned (boolean): parameter that flags if the pinned chats should or not be ignored - standard value: True (it will ignore pinned chats!)
        """
        try:
            search_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@id="side"]/div[1]/div/div/div/div')
                )
            )
            search_box.click()
            search_box.send_keys(Keys.ARROW_DOWN)
            chat = self.browser.switch_to.active_element
            time.sleep(1)
            if ignore_pinned:
                while True:
                    flag = False
                    for item in chat.find_elements(By.TAG_NAME, 'span'):
                        if "pinned" in item.get_attribute("innerHTML"):
                            flag = True
                            break
                    if not flag: break
                    chat.send_keys(Keys.ARROW_DOWN)
                    chat = self.browser.switch_to.active_element

            name = chat.text.split('\n')[0]
            # LOGGER.info(f"Successfully selected chat \"{name}\"")
            chat.send_keys(Keys.ENTER)

        except Exception as bug:
            garbage_val = 0
            # LOGGER.exception(f"Exception raised while getting first chat: {bug}")

    def search_chat_by_name(self, query: str):
        """search_chat_name()  [nCKbr]

        searches for the first chat containing the query parameter

        Args:
            query (string): query value to be located in the chat name
        """
        try:
            search_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@id="side"]/div[1]/div/div/div/div')
                )
            )
            search_box.click()
            search_box.send_keys(Keys.ARROW_DOWN)
            chat = self.browser.switch_to.active_element
            time.sleep(1)
            while True:
                name = chat.text.split('\n')[0]
                if query.upper() in name.upper():
                    break
                chat.send_keys(Keys.ARROW_DOWN)
                chat = self.browser.switch_to.active_element
            # LOGGER.info(f"Successfully selected chat \"{name}\"")
            chat.send_keys(Keys.ENTER)

        except Exception as bug:
            garbage_val = 0
            # LOGGER.exception(f"Exception raised while getting first chat: {bug}")

    def check_if_given_chat_has_unread_messages(self, query):
        """check_if_given_chat_has_unread_messages() [nCKbr]

        identifies if a given chat has unread messages or not.

        Args:
            query (string): query value to be located in the chat name
        """
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@id="pane-side"]/div[1]/div[1]/div[1]/child::div')
                )
            )
            list_of_messages = self.browser.find_elements_by_xpath(
                '//div[@id="pane-side"]/div[1]/div[1]/div[1]/child::div')

            for chat in list_of_messages:
                name = chat.text.split('\n')[0]
                if query.upper() in name.upper():
                    maybe_new_msg = chat.text.split('\n')[-1]
                    if maybe_new_msg and maybe_new_msg.isdigit():
                        # LOGGER.info(f"Yup, {maybe_new_msg} new message(s) on chat \"{name}\".")
                        return True
                    # LOGGER.info(f"There are no new messages on chat \"{query}\".")
                    return False

        except Exception as bug:
            garbage_val = 0
            # LOGGER.exception(f"Exception raised while getting first chat: {bug}")



    def send_message1(self, mobile: str, message: str) -> str:
        # CJM - 20220419:
        #   Send WhatsApp Message With Different URL, NOT using https://wa.me/ to prevent WhatsApp Desktop to open
        #   Also include the Number we want to send to
        #   Send Result
        #   0 or Blank or NaN = Not yet sent
        #   1 = Sent successfully
        #   2 = Number to short
        #   3 = Error or Failure to Send Message
        #   4 = Not a WhatsApp Number
        msg = f"0 "
        try:
            # Browse to a "Blank" message state
            self.browser.get(f"https://web.whatsapp.com/send?phone={mobile}&text")

            # This is the XPath of the message textbox

            inp_xpath = (
                '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]'
            )

            # inp_xpath = (
            #    '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]'
            # )

            # This is the XPath of the "ok button" if the number was not found
            nr_not_found_xpath = (
                '//*[@id="app"]/div/span[2]/div/span/div/div/div/div/div/div[2]/div/div'
            )

            # If the number is NOT a WhatsApp number then there will be an OK Button, not the Message Textbox
            # Test for both situations -> find_elements returns a List
            ctrl_element = self.wait.until(
                lambda ctrl_self: ctrl_self.find_elements(By.XPATH, nr_not_found_xpath)
                                  or ctrl_self.find_elements(By.XPATH, inp_xpath)
            )


            # Iterate through the list of elements to test each if they are a textBox or a Button

            for i in ctrl_element:
                if i.aria_role == "textbox":
                    # This is a WhatsApp Number -> Send Message

                    for line in message.split("\n"):
                        i.send_keys(line)
                        ActionChains(self.browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(
                            Keys.SHIFT).perform()
                    i.send_keys(Keys.ENTER)

                    msg = f"1 "  # Message was sent successfully
                    # Found alert issues when we send messages too fast, so I called the below line to catch any alerts
                    self.catch_alert()

                elif i.aria_role == "button":
                    # Did not find the Message Text box
                    # BUT we possibly found the XPath of the error "Phone number shared via url is invalid."
                    if i.text == "OK":
                        # This is NOT a WhatsApp Number -> Press enter and continue
                        i.send_keys(Keys.ENTER)
                        msg = f"4 "  # Not a WhatsApp Number

        except (NoSuchElementException, Exception) as bug:
            # LOGGER.exception(f"An exception occurred: {bug}")
            msg = f"Failed to send a message to {self.mobile}"

        finally:
            # LOGGER.info(f"{msg}")
            return msg

    def send_picture1(self, mobile: str, picture: str, message: str) -> str:
        msg=f"0 "

        try:

            self.browser.get(f"https://web.whatsapp.com/send?phone={mobile}&text")
            filename = os.path.realpath(picture)

            clip_button_path='//*[@id="main"]/footer//*[@data-icon="clip"]/..'

            nr_not_found_xpath = (
                '//*[@id="app"]/div/span[2]/div/span/div/div/div/div/div/div[2]/div/div'
            )

            ctrl_element = self.wait.until(
                lambda ctrl_self: ctrl_self.find_elements(By.XPATH, nr_not_found_xpath)
                                  or ctrl_self.find_elements(By.XPATH, clip_button_path)
            )

            for i in ctrl_element:
                if i.aria_role=='button':
                    if i.text=='OK':
                        i.send_keys(Keys.ENTER)
                        msg = f"4 "  # Not a WhatsApp Number
                        return msg

            clipButton = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="main"]/footer//*[@data-icon="clip"]/..')
                )
            )
            clipButton.click()

            imgButton = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="main"]/footer//*[@data-icon="attach-image"]/../input',
                    )
                )
            )
            imgButton.send_keys(filename)
            inp_xpath = '//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/div/div[1]/div[3]/div/div/div[2]/div/div[2]'
            input_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, inp_xpath))
            )
            for line in message.split("\n"):
                input_box.send_keys(line)
                ActionChains(self.browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(
                    Keys.SHIFT).perform()
            input_box.send_keys(Keys.ENTER)
            self.send_attachment1()

        except (NoSuchElementException, Exception) as bug:
            # LOGGER.exception(f"An exception occurred: {bug}")
            msg = f"Failed to send a message to {self.mobile}"

        finally:
        # LOGGER.info(f"{msg}")
           return msg

    def send_message(self, message):
        """send_message ()
        Sends a message to a target user

        Args:
            message ([type]): [description]
        """
        try:

            inp_xpath = (
                '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]'
            )

            # inp_xpath = (
            #    '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]'
            # )
            input_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, inp_xpath))
            )
            for line in message.split("\n"):
                input_box.send_keys(line)
                ActionChains(self.browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(
                    Keys.SHIFT).perform()
            input_box.send_keys(Keys.ENTER)
            # LOGGER.info(f"Message sent successfuly to {self.mobile}")
        except (NoSuchElementException, Exception) as bug:
            garbage_val = 0
            # LOGGER.exception(f"Failed to send a message to {self.mobile} - {bug}")
        finally:
            garbage_val = 0
            # LOGGER.info("send_message() finished running!")

    def find_attachment(self):
        clipButton = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="main"]/footer//*[@data-icon="clip"]/..')
            )
        )
        clipButton.click()

    def send_attachment(self):
        time.sleep(1)

        # Waiting for the pending clock icon to disappear

        # sendButton = self.wait.until(
        #    EC.presence_of_element_located(
        #        (
        #            By.XPATH,
        #            '//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/div/div[2]/div[2]/div/div/span',
        #        )
        #    )
        # )
        # sendButton.click()
        # Waiting for the pending clock icon to disappear again - workaround for large files or loading videos.
        # Appropriate solution for the presented issue. [nCKbr]
        time.sleep(3)

        # self.wait.until_not(
        #    EC.presence_of_element_located(
        #        (By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')
        #    )
        # )

    def send_attachment1(self):
        time.sleep(1)

        # Waiting for the pending clock icon to disappear
        try:
            while (True):
                e=self.browser.find_element(By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')
                time.sleep(1)
        except:
            garbage_val = 0

        # Waiting for the pending clock icon to disappear again - workaround for large files or loading videos.
        # Appropriate solution for the presented issue. [nCKbr]
        time.sleep(1)
        try:
            while (True):
                e = self.browser.find_element(By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')
                time.sleep(1)
        except:
            garbage_val = 0


    def send_picture(self, picture, message):
        """send_picture ()

        Sends a picture to a target user

        Args:
            picture ([type]): [description]
        """
        try:
            filename = os.path.realpath(picture)
            self.find_attachment()
            # To send an Image
            imgButton = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="main"]/footer//*[@data-icon="attach-image"]/../input',
                    )
                )
            )
            imgButton.send_keys(filename)
            inp_xpath = '//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/div/div[1]/div[3]/div/div/div[2]/div/div[2]'
            input_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, inp_xpath))
            )
            for line in message.split("\n"):
                input_box.send_keys(line)
                ActionChains(self.browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(
                    Keys.SHIFT).perform()
            input_box.send_keys(Keys.ENTER)
            self.send_attachment()
            # LOGGER.info(f"Picture has been successfully sent to {self.mobile}")
        except (NoSuchElementException, Exception) as bug:
            garbage_val = 0
            # LOGGER.exception(f"Failed to send a message to {self.mobile} - {bug}")
        finally:
            garbage_val = 0
            # LOGGER.info("send_picture() finished running!")

    def convert_bytes(self, size) -> str:
        # CJM - 2022/06/10:
        # Convert bytes to KB, or MB or GB
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return "%3.1f %s" % (size, x)
            size /= 1024.0

    def convert_bytes_to(self, size, to):
        # CJM - 2022 / 06 / 10:
        # Returns Bytes as 'KB', 'MB', 'GB', 'TB'
        conv_to = to.upper()
        if conv_to in ['BYTES', 'KB', 'MB', 'GB', 'TB']:
            for x in ['BYTES', 'KB', 'MB', 'GB', 'TB']:
                if x == conv_to:
                    return size
                size /= 1024.0

    def send_video(self, video):
        """send_video ()
        Sends a video to a target user
        CJM - 2022/06/10: Only if file is less than 14MB (WhatsApp limit is 15MB)

        Args:
            video ([type]): the video file to be sent.
        """
        import pdb;
        pdb.set_trace()
        try:
            filename = os.path.realpath(video)
            f_size = os.path.getsize(filename)
            x = self.convert_bytes_to(f_size, 'MB')
            if x < 14:
                # File is less than 14MB
                self.find_attachment()
                # To send a Video
                video_button = self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="main"]/footer//*[@data-icon="attach-image"]/../input',
                        )
                    )
                )

                video_button.send_keys(filename)

                self.send_attachment()
                # LOGGER.info(f"Video has been successfully sent to {self.mobile}")
            else:
                garbage_val = 0
                # LOGGER.info(f"Video larger than 14MB")
        except (NoSuchElementException, Exception) as bug:
            garbage_val = 0
            # LOGGER.exception(f"Failed to send a message to {self.mobile} - {bug}")
        finally:
            garbage_val = 0
            # LOGGER.info("send_video() finished running!")

    def send_file(self, filename):
        """send_file()

        Sends a file to target user

        Args:
            filename ([type]): [description]
        """
        try:
            filename = os.path.realpath(filename)
            self.find_attachment()
            document_button = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="main"]/footer//*[@data-icon="attach-document"]/../input',
                    )
                )
            )
            document_button.send_keys(filename)
            self.send_attachment()
        except (NoSuchElementException, Exception) as bug:
            garbage_val = 0
            # LOGGER.exception(f"Failed to send a file to {self.mobile} - {bug}")
        finally:
            garbage_val = 0
            # LOGGER.info("send_file() finished running!")

    def close_when_message_successfully_sent(self):
        """close_when_message_successfully_sent() [nCKbr]

        Closes the browser window to allow repeated calls when message is successfully sent/received.
        Ideal for recurrent/scheduled messages that would not be sent if a browser is already opened.
        [This may get deprecated when an opened browser verification gets implemented, but it's pretty useful now.]

        Friendly contribution by @euriconicacio.
        """

        # LOGGER.info("Waiting for message status update to close browser...")

        time.sleep(5)
        try:
            # Waiting for the pending clock icon shows and disappear
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')
                )
            )
            self.wait.until_not(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')
                )
            )
        except (NoSuchElementException, Exception) as bug:
            garbage_val = 0
            # LOGGER.exception(f"Failed to send a message to {self.mobile} - {bug}")
        finally:
            self.browser.close()
            # LOGGER.info("Browser closed.")


