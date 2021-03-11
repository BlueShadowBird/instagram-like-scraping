import csv
import json
import os
import pickle
from time import sleep

import requests


class InstagramScraper:
    def __init__(self):
        self.session = requests.session()

    def save_session(self, key):
        session_file = open('session/{}'.format(key), 'wb')
        pickle.dump(self.session, session_file)
        return True

    def load_session(self, key):
        session_file_string = 'session/{}'.format(key)
        if os.path.isfile(session_file_string):
            print('Login from session file')
            session_file = open(session_file_string, 'rb')
            self.session = pickle.load(session_file)
            print()
            return True
        else:
            return False

    def login(self, username, password):
        print('Do Login')

        url = 'https://www.instagram.com'
        self.session.headers.update({
            'User-Agent': 'Instagram 123.0.0.21.114 (iPhone; CPU iPhone OS 11_4 like Mac OS X; en_US; en-US; '
                          'scale=2.00; 750x1334) AppleWebKit/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Referer': 'https://www.instagram.com'
        })
        response: requests.Response = self.session.get(url)

        self.session.headers.update({'X-CSRFToken': response.cookies['csrftoken']})
        url = 'https://www.instagram.com/accounts/login/ajax/'
        params = {
            'username': username,
            'password': password
        }
        response = self.session.post(url, data=params, allow_redirects=True)

        if response.status_code == 200:
            if response.json()['authenticated']:
                self.session.cookies = response.cookies
                print('Login Success')
                return True
            print('Failed Login: authentication Fail')
            return False
        else:
            print('Failed Login:', response.status_code)
            print(response.text)
            return False

    def scrap_data(self, short_code):
        count = 0
        end_cursor = ''
        csv_writer = csv.writer(open('result/liked-by.csv', 'w+', encoding='utf8', newline=''))
        csv_writer.writerow(['User Name', 'Full Name', 'Profile pic'])
        while True:
            if count % 500 == 0 and count > 0:
                csv_writer = csv.writer(open('result/liked-by-{}.csv'.format(int(count / 500)+1), 'w+', encoding='utf8',
                                             newline=''))
                csv_writer.writerow(['User Name', 'Full Name', 'Profile pic'])
                print('\nscraped count {} like'.format(count))
            url = 'https://www.instagram.com/graphql/query/'
            variable = {
                'shortcode': short_code,
                'include_reel': True,
                'first': 50,
                'after': end_cursor
            }
            params = {
                'query_hash': 'd5d763b1e2acf209d62d22d184488e57',
                'variables': json.dumps(variable)
            }

            response = self.session.get(url, params=params)

            response_json = response.json()
            try:
                edges = response_json['data']['shortcode_media']['edge_liked_by']['edges']
            except Exception as e:
                print('There is error: ', e)
                sleep(20)
                continue

            for edge in edges:
                count += 1
                username = edge['node']['username']
                full_name = edge['node']['full_name']
                profile_pic = edge['node']['profile_pic_url']
                csv_writer.writerow({username, full_name, profile_pic})
            if not response_json['data']['shortcode_media']['edge_liked_by']['page_info']['has_next_page']:
                break

            print('-', end="")

            end_cursor = response_json['data']['shortcode_media']['edge_liked_by']['page_info']['end_cursor']
            sleep(2)
