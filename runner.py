from instagram_scraper import InstagramScraper

scraper = InstagramScraper()

username = input('enter username: ')
password = input('enter password: ')

if scraper.load_session(username) \
        or (scraper.login(username, password) and scraper.save_session(username)):
    while True:
        print(
            '\n===============================================\n'
            '1: Scrape Likes\n'
            '2: Scrape Comments'
            '3: Scrape Tag\n'
            '4: Scrape page\n'
            'else: Exit\n'
            '==============================================='
        )
        option = input('Choose what you want to scrape: ')

        if option == '1':
            short_code = input('enter short_code: ')
            scraper.scrape_like(short_code)
        elif option == '2':
            short_code = input('enter short_code: ')
            scraper.scrape_comments(short_code)
        elif option == '3':
            tag = input('enter tag: ')
            scraper.scrape_hashtag(tag)
        elif option == '4':
            page = input('enter page: ')
            scraper.scrape_page(page)
        else:
            break
else:
    print('Login Failed')
