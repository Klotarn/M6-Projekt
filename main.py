import modules.patch_instagram_scraper as patcher

patcher.apply_patches()

import modules.scrape as scrape
import json

# get usernames of accounts to scrape from accounts_to_scrape.json
accounts_to_scrape = []
with open("accounts_to_scrape.json", "r") as f:
    data = json.load(f)
    accounts_to_scrape = data.get("accounts", [])

print("Accounts to scrape:", accounts_to_scrape)

for account in accounts_to_scrape:
    res = scrape.scrape_account(account, 30)

    print("----------------\n")
    print(res["profile"]["username"], "(" + res["profile"]["full_name"] + ")")
    print("\n----------------\n")

    print(f"Posts:\n")
    for post in res["init_posts"]:
        print(f"{post['time']}: {post['text']}") # TODO - patch scraper to find shortcode and timestamp and print them here as well
        print()

    # for post in res["posts"]:
    #     print(f"{post['caption']}") # TODO - patch scraper to find shortcode and timestamp and print them here as well
    #     print()
