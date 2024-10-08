# welcome to my personal hell, wherein you will import image posts from reddit rss feeds, and then slap them onto mastodon. install requests, feedparser, mastodon.py, and beautifulsoup4 to make it all work. will require you make a virtual python env in order to for it run. when you've done all that, slap it into a cronjob and make sure you tell it to use that environment!

import os
import requests
import mastodon
from mastodon import Mastodon
import random
import tempfile
import praw
import time
from PIL import Image 

# list of common image file extensions
image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

# mastodon credentials
INSTANCE_URL = 'insert_instance_url_here'
CLIENT_ID = 'mastodon_client_id'
CLIENT_SECRET = 'mastodon_secret_key'
ACCESS_TOKEN = 'your_mastodon_access_token'

# reddit API credentials
REDDIT_CLIENT_ID = 'the_reddit_client_id'
REDDIT_CLIENT_SECRET = 'the_reddit_secret_key'
REDDIT_USER_AGENT = 'your_reddit_app_name'

# list your subreddits here, so that bot knows what to pick from
SUBREDDITS = [
    'science',
    'programming',
    'python',
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
        return high_res_photo_url, post_url, random_submission

def post_photo(mastodon_client, photo_url, post_url, submission):
    # download the image
    response = requests.get(photo_url)
    response.raise_for_status()  # ensure the request was successful

    # save the image to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(response.content)
        tmp_file_path = tmp_file.name

    try:
        # verify image integrity
        img = Image.open(tmp_file_path)
        img.verify()

        # post the image
        media = mastodon_client.media_post(media_file=tmp_file_path)

        # wait for media to finish processing
        while 'processing' in media and media['processing']:
            time.sleep(1)
            media = mastodon_client.media(media['id'])

        status_message = (
            f"░ Title: {submission.title}\n"
            f'░ Original post: {post_url}\n'
            f'░ Posted by: @{submission.author.name}@reddit.com\n'
            f'░ Your own text for whatever you want to write along with the above information can go here!'
        )
        mastodon_client.status_post(
            status=status_message,
            media_ids=[media['id']],
            sensitive=True,  # mark the post as sensitive
            spoiler_text="This is for the CW, can remove this completely if you don't want one"  # add spoiler text just in case
        )

    except Exception as e:
        print(f"Error verifying image: {e}")
        return

    finally:
        # delete the temporary file so that your hdd doesn't explode with anime girls and backrooms photos
        os.remove(tmp_file_path)

def resize_image(image, max_size):
    # resize the image to fit within the max_size limit while maintaining aspect ratio (mastodon likes it when you do this)
    width, height = image.size
    aspect_ratio = width / height
    new_width = int((max_size / (aspect_ratio * 3)) ** 0.5)
    new_height = int(new_width / aspect_ratio)
    return image.resize((new_width, new_height), Image.ANTIALIAS)

def follow_back(mastodon_client):
    followers = mastodon_client.account_followers(mastodon_client.me()['id'])
    for follower in followers:
        if not follower.get('following', False):
            mastodon_client.account_follow(follower['id'])
            print(f"Followed back: {follower['acct']}")

if __name__ == "__main__":
    # initialize Mastodon
    mastodon_client = Mastodon(
        access_token=ACCESS_TOKEN,
        api_base_url=INSTANCE_URL
    )

    # follow back new followers
    follow_back(mastodon_client)

    # initialize Reddit
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

    subreddit_name = get_random_subreddit()
    photo_url, post_url, submission = get_random_photo_from_subreddit(reddit, subreddit_name)
    post_photo(mastodon_client, photo_url, post_url, submission)

    # that's the end of the story, thanks for coming by!
