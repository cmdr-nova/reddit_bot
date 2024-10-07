Welcome to my personal hell, wherein you will import image posts from reddit rss feeds, and then slap them onto Mastodon. You don't like that? Too bad, you live with me now. 

First, you must acquire a server, unless you're going to run this on your own PC 24/7. That's up to you!

Install requests, feedparser, mastodon.py, and beautifulsoup4 to make it all work (use pip within an environment).

```
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip
```

```
cd /path/to/your/python-script-folder
python3 -m venv myenv
```
Hit the big red button,

```
source myenv/bin/activate
```

or if for some reason you're using stinky windows,

```
myenv\Scripts\activate
```

and then

```
pip install requests feedparser mastodon.py beautifulsoup4
```

Once you've done that, set us up the cronjob. Run it every 30 minutes, or whatever time you want.

```
*/30 * * * * /home/user/reddit-bot/myenv/bin/python /home/user/reddit-bot/reddit-bot.py
```

And there ya go.

(I'm still working out how to make the image quality not tiny and pixelated)
