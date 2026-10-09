from instagram_posts_scraper.instagram_posts_scraper import InstaPeriodScraper


def scrape_account(username, days_limit=30):
    ig_posts_scraper = InstaPeriodScraper()
    target_info = {"username": username, "days_limit": days_limit}
    res = ig_posts_scraper.get_posts(target_info=target_info)
    return res
