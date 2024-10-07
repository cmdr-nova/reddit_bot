# welcome to my personal hell, wherein you will import image posts from reddit rss feeds, and then slap them onto mastodon. install requests, feedparser, mastodon.py, and beautifulsoup4 to make it all work. will require you make a virtual pyton env in order to for it run. when you've done all that, slap it into a cronjob and make sure you tell it to use that environment!

import os
import requests
import mastodon
from mastodon import Mastodon
import random
import tempfile
import praw

# list of common image file extensions
image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

# mastodon credentials
INSTANCE_URL = 'your_instance_url'
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
ACCESS_TOKEN = 'your_access_token'

# Reddit API credentials
REDDIT_CLIENT_ID = 'your_client_id'
REDDIT_CLIENT_SECRET = 'your_client_secret'
REDDIT_USER_AGENT = 'your_client_name'

# list your subreddits here, so that bot knows what to pick from
SUBREDDITS = [
    'Animewallpaper',
    'ZeroTwo',
    'BlueArchive',
    'ZenlessZoneZero',
    'Edgerunners',
    'BaldursGate3',
    'BokuNoHeroAcademia',
    'ChainsawMan',
    'cosplaygirls',
    'backrooms',
    'AnimeGirls',
    '90sNostalgia',
    '2Booty',
    'animeART',
    'animetitties',
    'animefeets',
    'cosplaybabes',
    'cosplaylewd',
    'cosplaynsfw',
    'transgonewild',
    'gonewild',
    'liminalspace',
]

def get_random_subreddit():
    return random.choice(SUBREDDITS)

def get_high_res_image_url(submission):
    try:
        if submission.url.endswith(tuple(image_extensions)):
            return submission.url
        # check for preview images
        if hasattr(submission, 'preview'):
            images = submission.preview.get('images', [])
            if images:
                # get the highest resolution image
                resolutions = images[0].get('resolutions', [])
                if resolutions:
                    return resolutions[-1]['url']
    except Exception as e:
        print(f"Error fetching high-res image URL: {e}")
    return None

def get_random_photo_from_subreddit(reddit, subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    submissions = list(subreddit.hot(limit=50))  # fetch top 50 hot posts
    image_submissions = [submission for submission in submissions if get_high_res_image_url(submission)]

    if not image_submissions:
        print("No image posts found in subreddit. Retrying...")
        return get_random_photo_from_subreddit(reddit, subreddit_name)  # retry
    else:
        random_submission = random.choice(image_submissions)
        high_res_photo_url = get_high_res_image_url(random_submission)
        post_url = random_submission.url  # extract the post URL
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
            status='Put your own status text here! Original post: ' + post_url,
            media_ids=media,
            sensitive=True  # mark the post as sensitive, because that's the cool thing to do
        )
    finally:
        # delete the temporary file so that your hdd doesn't explode with anime girls and backrooms photos
        os.remove(tmp_file_path)

# follow users back function

def follow_back(mastodon_client):
    followers = mastodon_client.account_followers(mastodon_client.me().id)
    follower_ids = [follower.id for follower in followers]
    relationships = mastodon_client.account_relationships(follower_ids)
    for follower, relationship in zip(followers, relationships):
        if not relationship.following:
            mastodon_client.account_follow(follower.id)
            print(f"Followed back: {follower.username}")

def main():
    mastodon_client = mastodon.Mastodon(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        access_token=ACCESS_TOKEN,
        api_base_url=INSTANCE_URL
    )

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

    # follow back new followers
    follow_back(mastodon_client)

    subreddit_name = get_random_subreddit()
    photo_url, post_url = get_random_photo_from_subreddit(reddit, subreddit_name)
    if photo_url is None:
        print("Failed to get a valid photo URL. Exiting.")
        return
    post_photo(mastodon_client, photo_url, post_url)

if __name__ == '__main__':
    main()

# that's the end of the story, thanks for stopping by and have a great day!
