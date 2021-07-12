import time
import logging
import random
from urllib import parse
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException
from datetime import datetime

from yaudit.bot.driver_settings import *
from yaudit.exceptions import VideoNotAvailableException
from yaudit.database import session_scope
from yaudit.models import Bot as DatabaseBot, ViewAction, Video, Recommendation, SearchAction, SearchResult, Account,\
    Topic, Configuration, HomePageAction, HomePageResult

YOUTUBE_URL = 'https://www.youtube.com'


class Bot:
    def __init__(self, account_id=0, topic_id=0, configuration_id=0, full_run=True):
        account = Account.get_by_id(account_id)
        self.username = account.get('username')
        self.password = account.get('password')

        topic = Topic.get_by_id(topic_id)
        promoting_videos = topic.get('seed_videos', {}).get('promoting', [])
        debunking_videos = topic.get('seed_videos', {}).get('debunking', [])
        self.queries_to_check = topic.get('search_queries')

        configuration = Configuration.get_by_id(configuration_id)
        self.create_bubble_strategy = configuration.get('bubble_create_strategy')
        self.burst_bubble_strategy = configuration.get('bubble_burst_strategy')
        parameters = configuration.get('params', {})
        self.amount = parameters.get('watch_duration', 25.0)
        self.sleep_time = parameters.get('sleep_time', 0)
        num_of_videos_to_watch = parameters.get('number_of_videos', 20)
        self.query_frequency = parameters.get('query_frequency', 1)

        self.single_phase_video_count = num_of_videos_to_watch
        if self.create_bubble_strategy == 'explicit':
            self.interaction_type_create = parameters.get('interaction_type_create')
            self.interaction_frequency_create = parameters.get('interaction_frequency_create')
        if self.burst_bubble_strategy == 'explicit':
            self.interaction_type_burst = parameters.get('interaction_type_burst')
            self.interaction_frequency_burst = parameters.get('interaction_frequency_burst')

        promoting_videos = promoting_videos[:num_of_videos_to_watch]
        debunking_videos = debunking_videos[:num_of_videos_to_watch]
        random.shuffle(promoting_videos)
        random.shuffle(debunking_videos)
        if parameters.get('reverse', 'false') == 'true':
            message = 'Starting with debunking videos!'
            self.videos_to_watch = debunking_videos + promoting_videos
        else:
            message = 'Starting with promoting videos!'
            self.videos_to_watch = promoting_videos + debunking_videos

        self.driver, self.wait, self.stale_element_wait = initialize_driver()
        self.logger = logging.getLogger('FileLogger')
        self.run_headless = run_headless

        if full_run:
            self.logger.info(f'Starting with following settings:')
            self.logger.info(f' - {message}')
            self.logger.info(f' - watching {num_of_videos_to_watch} in each phase!')
            self.logger.info(f' - watch amount: {self.amount}')
            self.logger.info(f' - using {len(self.queries_to_check)} queries')
            self.logger.info(f' - sleep time between queries: {self.sleep_time}')
            self.logger.info(f' - querying after every {self.query_frequency} video')
            if self.create_bubble_strategy == 'explicit':
                self.logger.info(f' - using explicit action of {self.interaction_type_create} after every {self.interaction_frequency_create} video in creating phase!')
            if self.burst_bubble_strategy == 'explicit':
                self.logger.info(f' - using explicit action of {self.interaction_type_burst} after every {self.interaction_frequency_burst} video in bursting phase!')

        self.sequence_number = 1
        # Set google chrome session limit to 20 minutes
        self.session_limit = 2*60
        self.number_of_results = 20
        self.liked_videos = []

        if full_run:
            self.bot = DatabaseBot.create(account_id, topic_id, configuration_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_driver()

    def run(self):

        self.login()
        self.driver.get(YOUTUBE_URL)
        self.accept_cookies()

        self.logger.info(f'Obtaining homepage videos before run.')
        home_page_action = HomePageAction.create(self.bot.get('id'), self.__increase_sequence())
        home_page_videos = self.get_homepage_results()
        self.save_homepage_videos(home_page_videos, home_page_action)
        if (clarification := self.check_for_warning_message()) is not None:
            HomePageAction.update_warning_message(home_page_action.get('id'), clarification)
        self.logger.info(f'Using queries before run.')
        self.query_videos()

        for idx, video in enumerate(self.videos_to_watch):
            video_url = f'{YOUTUBE_URL}/watch?v={video.get("youtube_id")}'
            self.logger.info(f'Starting video number {idx + 1}!')
            try:
                view_action = ViewAction.create(self.bot.get('id'), video.get('video_id'), self.__increase_sequence())
                self.watch_video(video_url, self.amount)

                if idx < self.single_phase_video_count:
                    if self.create_bubble_strategy == 'explicit' and self.interaction_type_create == 'like' and (idx + 1) % self.interaction_frequency_create == 0:
                        success = self.like_video()
                        if success:
                            self.liked_videos.append(video_url)
                else:
                    if self.burst_bubble_strategy == 'explicit' and self.interaction_type_burst == 'like' and (idx + 1 - self.single_phase_video_count) % self.interaction_frequency_burst == 0:
                        success = self.like_video()
                        if success:
                            self.liked_videos.append(video_url)

                self.logger.info(f'Obtaining recommendation from {video_url}.')
                recommendations = self.get_recommended()
                self.save_recommendations(recommendations, view_action)
                if (clarification := self.check_for_warning_message()) is not None:
                    ViewAction.update_warning_message(view_action.get('id'), clarification)

                self.logger.info(f'Obtaining homepage videos after watching {video_url}.')
                home_page_action = HomePageAction.create(self.bot.get('id'), self.__increase_sequence())
                home_page_videos = self.get_homepage_results()
                self.save_homepage_videos(home_page_videos, home_page_action)
                if (clarification := self.check_for_warning_message()) is not None:
                    HomePageAction.update_warning_message(home_page_action.get('id'), clarification)

                if (idx + 1) % self.query_frequency == 0:
                    self.query_videos()
                    self.logger.info(f'Video number {idx + 1} finished!')
            except VideoNotAvailableException:
                self.logger.error(f'Video with url {video_url} not available! Skipping!')
                self.save_page_source(f'video_not_available-{video.get("youtube_id")}')
                continue
            except NoSuchElementException:
                self.logger.error(f'Unable to parse data from video with url {video_url}.')
                self.save_page_source(f'data_parsing-{video.get("youtube_id")}')
                continue

        self.clear_history()

    def login(self):
        success = False
        counter = 0
        while success is False and counter < 5:
            self.youtube_login()
            success = self.was_login_successful()
            counter += 1
        if not success:
            raise RuntimeError(f'The login was not successful.')

    def was_login_successful(self):
        checking_url = 'https://myactivity.google.com/item'
        self.driver.get(checking_url)
        time.sleep(0.25)
        return self.driver.current_url.count(checking_url) == 1

    def youtube_login(self):
        self.driver.get('https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?redirect_uri=https%3A%2F'
                        '%2Fdevelopers.google.com%2Foauthplayground&prompt=consent&response_type=code&client_id'
                        '=407408718192.apps.googleusercontent.com&scope=email&access_type=offline&flowName'
                        '=GeneralOAuthFlow')

        time.sleep(30)
        # Wait for page to load email field and `Next` button
        self.wait.until(visible((By.ID, 'identifierId')))
        self.wait.until(clickable((By.ID, 'identifierNext')))
        # Insert email into the field
        self.driver.find_element_by_id('identifierId').send_keys(self.username if self.username else os.getenv('YOUTUBE_USERNAME'))
        # Click `Next`
        self.driver.find_element_by_id('identifierNext').click()

        time.sleep(30)
        # Wait for page to load password field and `Login` button
        self.wait.until(visible((By.NAME, 'password')))
        self.wait.until(clickable((By.ID, 'passwordNext')))
        # Insert password into he field
        self.driver.find_element_by_name('password').send_keys(self.password if self.password else os.getenv('YOUTUBE_PASSWORD'))
        # Click `Login`
        self.driver.find_element_by_id('passwordNext').click()

        time.sleep(30)

    def clear_history(self):
        if self.create_bubble_strategy == 'explicit' or self.burst_bubble_strategy == 'explicit':
            self.clear_liked_videos()

        self.driver.get('https://myactivity.google.com/item')

        clicked = self.__open_clear_history_popup()

        if not clicked:
            # Wait until hamburger element on page loads and click it
            self.wait.until(visible((By.CSS_SELECTOR, 'div.gb_vc:nth-child(1)')))
            self.wait.until(clickable((By.CSS_SELECTOR, 'div.gb_vc:nth-child(1)')))
            self.driver.find_element_by_css_selector('div.gb_vc:nth-child(1)').click()
            self.__open_clear_history_popup()

        # Wait until the popup windows gets loaded
        self.wait.until(visible((By.CSS_SELECTOR, 'div.iZdpV')))
        self.wait.until(clickable((By.CSS_SELECTOR, 'div.iZdpV')))

        # Find link for deleting all history in choices and click it
        choice_list = self.driver.find_elements_by_css_selector('div.iZdpV')
        for choice in choice_list:
            if choice.text == 'Always' or choice.text == 'All time':
                choice.click()
                break

        # Wait until next part of popup window loads
        self.wait.until(visible((By.CSS_SELECTOR, 'div.Df8Did')))
        time.sleep(1)
        # Find all buttons
        buttons = self.driver.find_element_by_css_selector('div.Df8Did').find_elements_by_css_selector('span.VfPpkd-vQzf8d')
        for button in buttons:
            # In case there are multiple sources of history are present click `Next` and find `Delete` button to click
            if button.text == 'Next':
                # Click `Next`
                button.find_element_by_xpath('..').click()
                # Wait while new buttons load
                time.sleep(1)
                # Find all the buttons and click `Delete`
                other_buttons = self.driver.find_element_by_css_selector('div.Df8Did').find_elements_by_css_selector('span.VfPpkd-vQzf8d')
                for other_button in other_buttons:
                    if other_button.text == 'Delete':
                        other_button.find_element_by_xpath('..').click()
                        return
            # In case only one source of history is present click `Delete`
            elif button.text == 'Delete':
                button.find_element_by_xpath('..').click()
                break

    def accept_cookies(self):
        try:
            iframe = self.driver.find_element_by_xpath('//*[@id="iframe"]')
            self.driver.switch_to.frame(iframe)
            self.driver.find_element_by_xpath('//*[@id="introAgreeButton"]').click()
            self.driver.switch_to.default_content()
        except NoSuchElementException:
            self.logger.info('IFrame not found! Cookies already accepted.')

    def query_videos(self):
        random.shuffle(self.queries_to_check)
        for query_number, query in enumerate(self.queries_to_check):
            search_results_to_save = []
            self.logger.info(f'Using query "{query.get("query")}" with id {query.get("id")}')
            search_action = SearchAction.create(self.bot.get('id'), query.get('id'), self.__increase_sequence())
            self.search_query(query.get('query'))
            results = self.get_search_results()
            for idx, result in enumerate(results):
                extracted_uuid = self.__extract_uuid_from_url(result)
                if extracted_uuid is None:
                    continue
                video = Video.get_or_create(extracted_uuid)
                search_results_to_save.append(
                        SearchResult(idx + 1, search_action.get('id'), video.get('id'))
                )
            self.__save_database_objects_bulk(search_results_to_save)

            if (clarification := self.check_for_warning_message()) is not None:
                SearchAction.update_warning_message(search_action.get('id'), clarification)

            self.logger.info(f'Sleeping for {self.sleep_time} before next query!')
            time.sleep(self.sleep_time)

    def search_query(self, query):
        # TODO potentially implement more manual searching (using input and clicking)
        self.driver.get(f'{YOUTUBE_URL}/results?search_query={query}')

    def change_quality(self):
        time.sleep(1)
        attempts = 0
        while attempts < 5:
            try:
                # Wait until settings button is loaded and click it
                # self.stale_element_wait.until(clickable((By.CSS_SELECTOR, 'button.ytp-button.ytp-settings-button'))).click()
                self.driver.find_element_by_css_selector('button.ytp-button.ytp-settings-button').click()
                time.sleep(2)
                # Wait until settings window is loaded and click on quality
                self.stale_element_wait.until(clickable((By.XPATH, "//div[contains(text(),'Quality')]"))).click()
                time.sleep(2)
                # Wait until all qualities are loaded and select the 144p quality
                self.stale_element_wait.until(clickable((By.XPATH, "//span[contains(string(),'144p')]"))).click()
                return
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException):
                attempts += 1
                if attempts == 5:
                    self.logger.exception('Could not change quality')
                    return
            except Exception:
                self.logger.exception('Unknown error occured while changing quality!')
                return
        # self.driver.find_element_by_css_selector('button.ytp-button.ytp-settings-button').click()
        # time.sleep(2)
        # self.driver.find_element_by_xpath("//div[contains(text(),'Quality')]").click()
        # time.sleep(2)
        # self.driver.find_element_by_xpath("//span[contains(string(),'144p')]").click()

    def turn_off_autoplay(self):
        attempts = 0
        while attempts < 5:
            try:
                autoplay = self.driver.find_element_by_css_selector('div.ytp-autonav-toggle-button')
                is_autoplay_on = autoplay.get_attribute('aria-checked') == 'true'
                if is_autoplay_on:
                    autoplay.click()
                    is_autoplay_on = False
                return is_autoplay_on
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException):
                attempts += 1
                if attempts == 5:
                    self.logger.exception('Could not turn off autoplay')
                    return True

    def watch_video(self, url, amount):
        self.driver.get(url)
        self.logger.info(f'Watching video {url}.')
        time.sleep(2)

        # Calculate how many seconds we need to watch
        duration = int(self.driver.execute_script("return document.getElementById('movie_player').getDuration()"))
        watch_whole_video = False
        if amount > 1.0:
            seconds_to_watch = int(min(amount, duration))
        else:
            # Calculate the seconds as percentage of the whole duration of video
            seconds_to_watch = int(duration * amount)

        if seconds_to_watch >= duration:
            watch_whole_video = True

        self.change_quality()

        self.logger.info(f'The amount to watch is {seconds_to_watch}!')
        old_current_time = int(self.driver.execute_script("return document.getElementById('movie_player').getCurrentTime()"))
        time.sleep(1)
        current_time = int(self.driver.execute_script("return document.getElementById('movie_player').getCurrentTime()"))
        if old_current_time != current_time:
            try:
                # Wait until video buttons load
                self.stale_element_wait.until(clickable((By.XPATH, "//button[@aria-label='Play (k)']")))
                # Click play
                self.driver.find_element_by_xpath("//button[@aria-label='Play (k)']").click()
            except (TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException):
                current_time = self.driver.execute_script("return document.getElementById('movie_player').getCurrentTime()")
                if not current_time > 0:
                    self.logger.error(f'Could not start video with url {url}!')
                    extracted_uuid = self.__extract_uuid_from_url(url)
                    self.save_page_source(f'watch-{extracted_uuid if extracted_uuid is not None else "missing"}')
                    return

        is_autoplay_on = self.turn_off_autoplay()

        # Wait until the requested amount of seconds is watched
        current_time = int(self.driver.execute_script("return document.getElementById('movie_player').getCurrentTime()"))
        watch_time_while_sleeping = (seconds_to_watch - current_time) * 0.95
        count = 0
        while current_time < watch_time_while_sleeping:
            if count >= 20:
                break
            time_left_to_watch = (watch_time_while_sleeping - current_time)
            time_to_sleep = min(self.session_limit, time_left_to_watch)
            self.logger.info(f'Amount still not watched. Sleeping for {time_to_sleep}')
            time.sleep(time_to_sleep if time_to_sleep > 0 else 0)
            current_time = int(self.driver.execute_script("return document.getElementById('movie_player').getCurrentTime()"))
            self.logger.info(f'Already watched {current_time} from the video!')
            count += 1

        count = 0
        while current_time < seconds_to_watch:
            if count >= 20:
                break
            time.sleep(5)
            current_time = int(self.driver.execute_script("return document.getElementById('movie_player').getCurrentTime()"))
            count += 1

        # Pause the video
        self.logger.info(f'Watched given amount of {seconds_to_watch} from video {url}. Pausing.')
        if is_autoplay_on:
            if current_time >= duration:
                self.driver.find_element_by_css_selector('button.ytp-upnext-cancel-button').click()
            else:
                self.driver.find_element_by_xpath("//button[@aria-label='Pause (k)']").click()

    def get_recommended(self):
        """
            Obtains urls for all the recommended videos in the currently playing video. They are ordered according to
            the recommendation position.
            :return: list of video urls in the order of recommendation.
        """
        self.wait.until(presence((By.ID, "related")))
        related = self.wait.until(visible((By.ID, "related")))

        self.save_page_source('recommendations')
        links = self.__wait_for_number_of_results(self.number_of_results, related, 'recommendations')
        return links[:20]

    def get_search_results(self):
        """
            Obtains urls for all the videos from the search results. They are ordered according to
            the position in the results.
            :return: list of video urls in the order as they were returned in the search.
        """
        count = 0
        while count < 5:
            try:
                self.wait.until(presence((By.ID, 'contents')))
                break
            except TimeoutException:
                if count < 5:
                    count += 1
                else:
                    raise
        results = self.wait.until(visible((By.ID, 'contents')))

        self.save_page_source('search')
        video_links = self.__wait_for_number_of_results(self.number_of_results, results, 'search')

        return video_links

    def get_homepage_results(self):
        """
            Obtains urls for all the videos from the homepage. They are ordered according to
            the position in the homepage from left.
            :return: list of video urls in the order as they were shown on the homepage.
        """
        self.driver.get(YOUTUBE_URL)
        count = 0
        while count < 5:
            try:
                self.wait.until(presence((By.ID, 'contents')))
                break
            except TimeoutException:
                if count < 5:
                    count += 1
                else:
                    raise
        results = self.wait.until(visible((By.ID, 'contents')))

        self.save_page_source('homepage')
        video_links = self.__wait_for_number_of_results(self.number_of_results, results, 'homepage')

        return video_links

    def close_driver(self):
        self.driver.close()

    def save_page_source(self, name=None):
        path = f'htmls/' \
               f'config_{os.getenv("YAUDIT_CONFIGURATION_ID", 0)}' \
               f'-topic_{os.getenv("YAUDIT_TOPIC_ID", 0)}' \
               f'-acc_{os.getenv("YAUDIT_ACCOUNT_ID", 0)}'
        os.makedirs(path, exist_ok=True)
        filename = f'{datetime.now()}{f"-{name}" if name is not None else ""}'

        with open(os.path.join(path, f'{filename}.html'), 'w') as file:
            file.write(self.driver.page_source)

        if not self.run_headless:
            success = False
            count = 0
            while not success:
                try:
                    self.driver.save_screenshot(os.path.join(path, f'{filename}.png'))
                    success = True
                    break
                except TimeoutException:
                    if count >= 5:
                        self.logger.exception(f'Could not take screenshot!')
                        break
                    count += 1

    def save_recommendations(self, recommendations, view_action):
        recommendation_objects = []
        for idx, recommendation in enumerate(recommendations):
            extracted_uuid = self.__extract_uuid_from_url(recommendation)
            if extracted_uuid is None:
                continue
            video = Video.get_or_create(extracted_uuid)
            recommendation_objects.append(
                    Recommendation(idx + 1, view_action.get('id'), video.get('id'))
            )
        self.__save_database_objects_bulk(recommendation_objects)

    def save_homepage_videos(self, results, home_page_action):
        homepage_objects = []
        for idx, result in enumerate(results):
            extracted_uuid = self.__extract_uuid_from_url(result)
            if extracted_uuid is None:
                continue
            video = Video.get_or_create(extracted_uuid)
            homepage_objects.append(
                    HomePageResult(idx + 1, home_page_action.get('id'), video.get('id'))
            )
        self.__save_database_objects_bulk(homepage_objects)

    def check_for_warning_message(self):
        """
            Checks for presence of Youtube clarification message for Covid-19 and other topics.
        """
        clarification_renderers = self.driver.find_elements_by_css_selector('div.ytd-clarification-renderer')
        if clarification_renderers:
            clarification = clarification_renderers[0].find_element_by_xpath('..')
            return clarification.get_attribute('outerHTML')
        
        info_renderers = self.driver.find_elements_by_css_selector('div.ytd-info-panel-content-renderer')
        if info_renderers:
            info = info_renderers[0].find_element_by_xpath('..')
            return info.get_attribute('outerHTML')

        return None

    def like_video(self):
        count = 0
        while count < 5:
            try:
                success = self.interact_with_like_button(like=True)
                if success:
                    return success
                else:
                    count += 1
            except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
                count += 1
                if count >= 5:
                    self.logger.exception(f'Could not like video!')
                    raise
        return False

    def remove_like_from_video(self):
        try:
            success = self.interact_with_like_button(like=False)
            if not success:
                self.logger.exception(f'Could not remove like from video!')
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            self.logger.exception(f'Could not remove like from video!')
            raise

    def interact_with_like_button(self, like=True):
        like_button = self.__find_like_button()
        liked = like_button.get_attribute('aria-pressed')
        try:
            if (like and liked == 'false') or (not like and liked == 'true'):
                like_button.click()
            else:
                self.logger.warning(f'Could not perform requested action of {"liking" if like else "disliking"}. Actions was already performed!')
                return True
        except (ElementNotInteractableException, ElementClickInterceptedException):
            self.driver.execute_script("arguments[0].click();", like_button)
        return like_button.get_attribute('aria-pressed') != liked

    def clear_liked_videos(self):
        self.driver.get('https://www.youtube.com/playlist?list=LL')
        time.sleep(5)
        videos = self.driver.find_elements_by_css_selector('div#content.ytd-playlist-video-renderer')
        time.sleep(5)
        for video in videos[::-1]:
            video.find_element_by_xpath('..').find_element_by_css_selector('button#button').click()
            time.sleep(2)
            items = self.driver.find_element_by_css_selector('tp-yt-paper-listbox#items').find_elements_by_css_selector('tp-yt-paper-item.ytd-menu-service-item-renderer')
            for item in items[::-1]:
                if item.text == 'Remove from Liked videos':
                    item.click()
                    time.sleep(2)
                    break   


    def __find_like_button(self):
        menu = self.driver.find_element_by_css_selector('div#menu-container')
        buttons = menu.find_elements_by_css_selector('button.yt-icon-button')
        for elem in buttons:
            label = elem.get_attribute('aria-label')
            if 'like' in label and 'dislike' not in label:
                return elem

    def __check_video_availability(self):
        error_containers = self.driver.find_elements_by_css_selector('.yt-player-error-message-renderer')
        if len(error_containers):
            raise VideoNotAvailableException

    def __increase_sequence(self):
        sequence = self.sequence_number
        self.sequence_number += 1
        return sequence

    def __extract_uuid_from_url(self, url):
        url_data = parse.urlparse(url)
        query = parse.parse_qs(url_data.query)
        if query.get('v', []):
            uuid = query["v"][0]
            return uuid
        else:
            return None

    def __wait_for_number_of_results(self, number, container, page_source_name):
        count = 0
        video_links = self.__wait_until_videos_load(container)
        while len(video_links) < number:
            if count >= 5:
                self.logger.exception(f'Cannot retrieve videos from {page_source_name}, retrieved {len(video_links)}')
                break
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight || document.documentElement.scrollHeight);")
            time.sleep(2)
            video_links = self.__wait_until_videos_load(container)
            count += 1
        
        self.save_page_source(page_source_name)

        link_results = []
        for link in video_links:
            if link is not None:
                href = link.find_element_by_css_selector('a').get_attribute('href')
                if href not in link_results:
                    link_results.append(href)
        return link_results

    def __wait_until_videos_load(self, container):
        links = []
        video_counter = 0
        old_video_counter = 1
        counter = 0

        while video_counter != old_video_counter and counter < 10:
            if video_counter == old_video_counter:
                time.sleep(1.0)
                counter += 1
            links = container.find_elements_by_id("dismissible")
            old_video_counter = video_counter
            video_counter = len(links)

        return links

    def __open_clear_history_popup(self):
        # Wait until menu opens and find link for deleting all activity
        self.wait.until(visible((By.CSS_SELECTOR, 'a.IlZEuc')))
        self.wait.until(clickable((By.CSS_SELECTOR, 'a.IlZEuc')))
        navigation_menu_links = self.driver.find_elements_by_css_selector('.IlZEuc')
        for link in navigation_menu_links:
            if link.text == 'Delete activity by':
                # Check if menu is open
                try:
                    link.click()
                    return True
                except ElementNotInteractableException:
                    self.driver.find_element_by_css_selector('div.gb_vc:nth-child(1)').click()
                    link.click()
                    return True
        return False

    def __save_database_objects_bulk(self, database_objects):
        with session_scope() as session:
            for database_object in database_objects:
                session.add(database_object)
