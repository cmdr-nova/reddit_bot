# welcome to my personal hell, wherein you will import image posts from reddit rss feeds, and then slap them onto reddit. install requests, feedparser, mastodon.py, and beautifulsoup4 to make it all work. will require you make a virtual pyton env in order to for it run. when you've done all that, slap it into a cronjob and make sure you tell it to use that environment!

import os
import requests
import feedparser
import mastodon
from mastodon import Mastodon
import random
import tempfile
from bs4 import BeautifulSoup

# file extensions for images that are referenced 
image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

# this is where you put your mastodon credentials so that the bot can post, you'll get this from the developer section in the account's preferences after you've created an app for it

INSTANCE_URL = 'your_masto_url'
CLIENT_ID = 'the_masto_client_key'
CLIENT_SECRET = 'the_super_secret_masto_client_key'
ACCESS_TOKEN = 'plop_in_the_access_token_here'

# list your feeds here, so that bot knows what to pick from. i've included my own, but you can replace them with whatever you want, or even reduce it to just one feed!
    
SUBREDDIT_RSS_FEEDS = [
    'https://www.reddit.com/r/Animewallpaper.rss',
    'https://www.reddit.com/r/ZeroTwo.rss',
    'https://www.reddit.com/r/BlueArchive.rss',
    'https://www.reddit.com/r/ZenlessZoneZero.rss',
    'https://www.reddit.com/r/Edgerunners.rss',
    'https://www.reddit.com/r/BaldursGate3.rss',
    'https://www.reddit.com/r/BokuNoHeroAcademia.rss',
    'https://www.reddit.com/r/ChainsawMan.rss',
    'https://www.reddit.com/r/cosplaygirls.rss',
    'https://www.reddit.com/r/backrooms.rss',
    'https://www.reddit.com/r/AnimeGirls.rss',
    'https://www.reddit.com/r/90sNostalgia.rss',
    'https://www.reddit.com/r/2Booty.rss',
]

# start yer engines, counterstrike gamers

def get_random_rss_feed():
    return random.choice(SUBREDDIT_RSS_FEEDS)

def extract_image_url(post):
    # check for media content
    if 'media_content' in post:
        for media in post['media_content']:
            if any(media['url'].endswith(ext) for ext in image_extensions):
                return media['url']
    
    # check for image links in content
    if 'content' in post:
        for content in post['content']:
            soup = BeautifulSoup(content['value'], 'html.parser')
            img_tag = soup.find('img')
            if img_tag and any(img_tag['src'].endswith(ext) for ext in image_extensions):
                return img_tag['src']
    
    # check for image links in summary
    if 'summary' in post:
        soup = BeautifulSoup(post['summary'], 'html.parser')
        img_tag = soup.find('img')
        if img_tag and any(img_tag['src'].endswith(ext) for ext in image_extensions):
            return img_tag['src']
    
    return None

def get_high_res_image_url(url):
    # attempt to get a higher resolution image by modifying the URL
    if 'preview.redd.it' in url:
        url = url.replace('preview', 'i')
    # remove any parameters that might limit the quality
    url = url.split('?')[0]
    return url

def get_random_photo_from_feed(feed_url):
    feed = feedparser.parse(feed_url)
    image_posts = [post for post in feed.entries if extract_image_url(post)]

    if not image_posts:
        print("No image posts found in feed. Retrying...")
        return get_random_photo_from_feed(feed_url)  # retry
    else:
        random_post = random.choice(image_posts)
        photo_url = extract_image_url(random_post)
        high_res_photo_url = get_high_res_image_url(photo_url)
        post_url = random_post.link  # extract the post URL
        return high_res_photo_url, post_url

def post_photo(mastodon_client, photo_url, post_url):
    # download the image
    response = requests.get(photo_url)
    response.raise_for_status()  # ensure the request was successful

    # save the image to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(response.content)
        tmp_file_path = tmp_file.name

    try:
        # post the image
        media = mastodon_client.media_post(media_file=tmp_file_path)
        mastodon_client.status_post(
            status='this is what the bot will post as a status, edit this line! (keep the original post section, though) Original post: ' + post_url,
            media_ids=media,
            sensitive=True  # mark the post as sensitive, because that's the cool thing to do
        )
    finally:
        # delete the temporary file so that your hdd doesn't explode with anime girls and backrooms photos
        os.remove(tmp_file_path)

def main():
    mastodon_client = mastodon.Mastodon(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        access_token=ACCESS_TOKEN,
        api_base_url=INSTANCE_URL
    )

    feed_url = get_random_rss_feed()
    photo_url, post_url = get_random_photo_from_feed(feed_url)
    post_photo(mastodon_client, photo_url, post_url)

if __name__ == '__main__':
    main()

# that's the end of the story, thanks for stopping by and have a great day!
