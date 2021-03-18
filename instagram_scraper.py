import csv
import json
import os
import pickle
from datetime import datetime
from time import sleep

import requests


def __two_digit__(digit):
    if digit < 10:
        return '0{}'.format(digit)
    return digit


class InstagramScraper:
    def __init__(self):
        self.session = requests.session()
        now = datetime.now()
        self.base_result_dir = 'result/{}{}{}-{}{}{}'.format(__two_digit__(now.year), __two_digit__(now.month),
                                                             __two_digit__(now.day), __two_digit__(now.hour),
                                                             __two_digit__(now.minute), __two_digit__(now.second))
        os.mkdir(self.base_result_dir)

    def save_session(self, key):
        session_file = 'session/{}'.format(key)
        if os.path.exists(session_file):
            os.remove(session_file)
        session_file = open(session_file, 'wb')
        pickle.dump(self.session, session_file)
        return True

    def load_session(self, key):
        session_file_string = 'session/{}'.format(key)
        if os.path.isfile(session_file_string):
            print('Login from session file')
            session_file = open(session_file_string, 'rb')
            self.session = pickle.load(session_file)
            return True
        else:
            return False

    def is_login(self):
        resp = self.session.get('https://www.instagram.com')
        # print(resp.text)
        if resp.status_code == 200:
            # and '\nLogin • Instagram\n' != BeautifulSoup(resp.text, 'html.parser').title.text:
            print('Login True')
            self.session.cookies = resp.cookies
            return True
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
        resp: requests.Response = self.session.get(url)

        self.session.headers.update({'X-CSRFToken': resp.cookies['csrftoken']})
        url = 'https://www.instagram.com/accounts/login/ajax/'
        params = {
            'username': username,
            'password': password
        }
        resp = self.session.post(url, data=params, allow_redirects=True)

        if resp.status_code == 200:
            if resp.json()['authenticated']:
                self.session.cookies = resp.cookies
                print(resp.text)
                print('Login Success')
                return True
            print('Failed Login: authentication Fail')
            return False
        else:
            print('Failed Login:', resp.status_code)
            print(resp.text)
            return False

    def scrape_like(self, short_code):
        count = 0
        end_cursor = ''
        csv_writer = csv.writer(open('{}/liked-by.csv'.format(self.base_result_dir), 'w+', encoding='utf8', newline=''))
        csv_writer.writerow(['User Name', 'Full Name', 'Profile pic'])
        while True:
            if count % 500 == 0 and count > 0:
                csv_writer = csv.writer(
                    open('{}/liked-by-{}.csv'.format(self.base_result_dir, int(count / 500) + 1), 'w+', encoding='utf8',
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

            resp = self.session.get(url, params=params)

            response_json = resp.json()
            try:
                edge_liked_by = response_json['data']['shortcode_media']['edge_liked_by']
            except Exception as e:
                print('There is error: ', e)
                sleep(20)
                continue

            for edge in edge_liked_by['edges']:
                count += 1
                username = edge['node']['username']
                full_name = edge['node']['full_name']
                profile_pic = edge['node']['profile_pic_url']
                csv_writer.writerow({username, full_name, profile_pic})
            if not edge_liked_by['page_info']['has_next_page']:
                break

            print('-', end="")

            end_cursor = edge_liked_by['page_info']['end_cursor']
            sleep(2)

        print('\nscraped count {} like'.format(count))

    def scrape_comments(self, short_code):
        count = 0
        end_cursor = ''
        csv_writer = csv.writer(open('{}/comments.csv'.format(self.base_result_dir), 'w+', encoding='utf8', newline=''))
        csv_writer.writerow(['No', 'Id', 'Username', 'text'])
        while True:
            if count % 500 == 0 and count > 0:
                csv_writer = csv.writer(
                    open('result/comments-{}.csv'.format(int(count / 500) + 1), 'w+', encoding='utf8',
                         newline=''))
                csv_writer.writerow(['No', 'Id', 'Username', 'text'])
                print('\nscraped count {} comments'.format(count))
            url = 'https://www.instagram.com/graphql/query/'
            variable = {
                'shortcode': short_code,
                'first': 50,
                'after': end_cursor
            }
            params = {
                'query_hash': 'bc3296d1ce80a24b1b6e40b1e72903f5',
                'variables': json.dumps(variable)
            }

            resp = self.session.get(url, params=params)
            response_json = resp.json()
            try:
                edge_media_to_parent_comment = response_json['data']['shortcode_media']['edge_media_to_parent_comment']
            except Exception as e:
                print('There is error: ', e)
                sleep(20)
                continue

            for edge in edge_media_to_parent_comment['edges']:
                count += 1
                comment_id = edge['node']['id']
                text = edge['node']['text']
                username = edge['node']['owner']['username']
                csv_writer.writerow([count, comment_id, username, text])
            if not edge_media_to_parent_comment['page_info']['has_next_page']:
                break

            print('-', end="")

            end_cursor = edge_media_to_parent_comment['page_info']['end_cursor']
            sleep(2)

        print('\nscraped count {} comments'.format(count))

    def scrape_hashtag(self, tag):
        count = 0
        end_cursor = ''
        while True:
            if count % 500 == 0 and count > 0:
                print('\nscraped count {} comments'.format(count))

            url = 'https://www.instagram.com/explore/tags/{}/?__a=1&max_id='.format(tag, end_cursor)

            resp = self.session.get(url)
            response_json = resp.json()
            try:
                edge_hashtag_to_media = response_json['graphql']['hashtag']['edge_hashtag_to_media']
            except Exception as e:
                print('There is error: ', e)
                sleep(20)
                continue

            for edge in edge_hashtag_to_media['edges']:
                self.scrape_post_detail(edge['node']['shortcode'])
                count += 1
                print('scraped {} detail(s)'.format(count))
            if not edge_hashtag_to_media['page_info']['has_next_page']:
                break
            print(count)

            end_cursor = edge_hashtag_to_media['page_info']['end_cursor']
            sleep(2)

        print('\nscraped count {} comments'.format(count))

    def scrape_page(self, page):
        count = 0
        end_cursor = ''
        while True:
            if count % 500 == 0 and count > 0:
                print('\nscraped count {} comments'.format(count))

            url = 'https://www.instagram.com/{}/?__a=1&max_id='.format(page, end_cursor)
            print(url
                  )
            resp = self.session.get(url)
            response_json = resp.json()
            try:
                edge_owner_to_timeline_media = response_json['graphql']['user']['edge_owner_to_timeline_media']
            except Exception as e:
                print('There is error: ', e)
                sleep(20)
                continue

            for edge in edge_owner_to_timeline_media['edges']:
                self.scrape_post_detail(edge['node']['shortcode'])
                count += 1
                print('scraped {} detail(s)'.format(count))
            if not edge_owner_to_timeline_media['page_info']['has_next_page']:
                break
            print(count)

            end_cursor = edge_owner_to_timeline_media['page_info']['end_cursor']
            sleep(2)

        print('\nscraped count {} comments'.format(count))

    def scrape_post_detail(self, short_code):
        print('scraping short_code: {}'.format(short_code))
        url = 'https://www.instagram.com/p/{}/?__a=1'.format(short_code)
        resp_json = self.session.get(url).json()
        shortcode_media = resp_json['graphql']['shortcode_media']

        is_video = shortcode_media['is_video']
        username = shortcode_media['owner']['username']
        edges_caption = shortcode_media['edge_media_to_caption']['edges']
        if len(edges_caption) > 0:
            caption = edges_caption[0]['node']['text']
        else:
            caption = ''

        path = '{}/{}/'.format(self.base_result_dir, short_code)
        os.mkdir(path)
        if is_video:
            vid_url = shortcode_media['video_url']
            open('{}video.mp4'.format(path), 'wb').write(self.session.get(vid_url).content)
        else:
            if 'edge_sidecar_to_children' in shortcode_media:
                img_count = 0
                edge_sidecar_to_children = shortcode_media['edge_sidecar_to_children']
                for edge in edge_sidecar_to_children['edges']:
                    img_count += 1
                    pic_url = edge['node']['display_resources'][0]['src']
                    file_name = '{}.jpg'.format(img_count)
                    open('{}/picture-{}'.format(path, file_name), 'wb').write(self.session.get(pic_url).content)
            else:
                pic_url = shortcode_media['display_resources'][0]['src']
                open('{}/picture.jpg'.format(path), 'wb').write(self.session.get(pic_url).content)

        open('{}/{}.txt'.format(path, username), 'w+', encoding='utf8', newline='').write(caption)
        print('scrape short_code: {} done'.format(short_code))
