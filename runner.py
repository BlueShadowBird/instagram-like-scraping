from instagram_scraper import InstagramScraper

scraper = InstagramScraper()

username = input('enter username: ')
password = input('enter password: ')
short_code = input('enter short code: ')

if scraper.load_session(username) or (scraper.login(username, password) and scraper.save_session(username)):
    scraper.scrap_data(short_code)
