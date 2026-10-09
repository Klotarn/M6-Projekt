from instagram_posts_scraper.parse import Parser


def patched_extract_info_value(item_in):
    if item_in is None:
        return None
    num = item_in.find("div", class_="num")
    if num is None:
        return None
    return num.text.strip()


def patched_get_counts_of_posts(profile_soup):
    item_posts = profile_soup.find("div", class_="counts")

    if item_posts is None:
        return None  # eller 0

    return Parser.extract_info_value(item_in=item_posts)


def apply_patches():
    Parser.extract_info_value = staticmethod(patched_extract_info_value)
    Parser.get_counts_of_posts = staticmethod(patched_get_counts_of_posts)
