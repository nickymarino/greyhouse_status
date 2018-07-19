import tweepy
import pushover
import random
import time
import os
from datetime import datetime, timedelta
from dateutil import tz

# Validate that Twitter API keys can be imported
try:
	from greyhouse_status_keys import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET
except ImportError:
	print('Could not get required keys from greyhouse_status_keys.py')
# Check if we're using Pushover
try:
	from pushover_keys import PUSHOVER_USER, PUSHOVER_APP_TOKEN
	use_pushover = True
except ImportError:
	use_pushover = False

def get_responses():
	'''Returns a dictionary of responses, each item an array of one category of responses'''
	responses = {}

	# Text responses
	responses['default'] = [
		'No.',
		'Nope.',
		'Nah fam',
		'Lol nope',
		'Lol nope 😂',
		'Hell nah',
		'Hell no',
		'HAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHA no',
		'Bitch you thought',
		'You wish',
		'You\'re gonna get riggity riggity wrecked',
		'Keep dreaming',
		'Every table\'s taken, sry bb',
		'Maybe? Like 1 or 2?',
		'*Rolls dice* ...Nope',
		'Don\'t even bother.',
		'Wait there\'s one! ...Oh someone just sat down :/',
		'-1',
		'Well, there\'s three tables with only one person sitting at each.',
		'Some seats have just opened up in the bathroom! Stalls 2 and 3.',
		'Honestly, just sit on the floor',
		'BYOC if you want a chair. Don\'t be such a mooch.',
		'You know what, just go to Vienna',
		'Lol',
		'Really slow right now, tons of seats. Haha in your dreams',
		'Guess you\'re gettin it to go',
		'Nope, the same 20 people have been here for the past hour, probably aren\'t leaving soon',
		'If you\'re willing to throw elbows, tons!',
		'No seats available until 10pm!',
		'Current wait time: TBD',
		'$7 for a cup of coffee, and you can\'t even sit down...',
		'Even with 280 characters, there\'s still not enough room here.',
		'Lolz you wish, scrub',
		'What do you think?\n\n\n...no',
		'Bitch you wish',
		'All I want for Christmas is a seat at Greyhouse',
		'IU SUCKS!\n\n...And Greyhouse is still full',
		('.\n' * 200) + '...no seats open.',
		'Shoulda gotten here earlier, scrub',
		'😂😂😂😂😂',
		'absolutely not :(',
		'Game over. Please insert coin.',
		'Eventually maybe',
		'Honestly, just go to Vienna. They have seats.',
		'Lolololol',
		'Just sit on someone else',
		'Somehow WALC has more seats',
		'Not gonna happen, bud',
		'Just give up',
		'They\'re not even open right now!',
		'Standing room only',
	] + get_files_in_folder('./media')
	
	# Responses when the store is closed
	responses['closed'] = [
		'Well there would be seats open, but we\'re closed',
		'Closed. Rip',
		'Wait, every single chair is empty?! Oh we\'re closed',
	]

	# Responses when the store opens
	responses['opened'] = [
		'Just opened! Get \'em while they\'re hot!',
		'Open for business! Seats will be full in about 3 minutes.',
		'Hurry! We just opened so there\'s about 4 seats left!',
	]

	return responses

def get_files_in_folder(folder):
	'''Returns an array of filenames directly under folder'''
	return [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

def get_connection():
	'''Returns an authenticated Tweepy API object'''
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth)

	# Validate keys
	if not api.verify_credentials():
		raise IOError('Twitter API keys are invalid')
	return api

def send_tweet(string):
	'''Sends a tweet with media if the string is a valid file path, sends the string as a tweet otherwise'''
	api = get_connection()	
	# Send tweet
	try:
		if os.path.isfile(string):
			status = api.update_with_media(string)
		else:
			status = api.update_status(string)
		print('Tweet "{}" sent at {}'.format(string, status.created_at))
	except tweepy.TweepError as ex:
		if (hasattr(ex, 'message')) and (ex.message[0]['code'] != 187): # Duplicate status/tweet
			raise Exception('Tweet "{}" could not be sent. Error below:\n{}'.format(string, ex))

def write_to_log(old_log_arr, new_text):
	# Only keep a limited amount of history in the log
	num_responses_stored = 50
	if len(old_log_arr) >= num_responses_stored:
		log_data = [new_text] + old_log_arr[0:(num_responses_stored-1)]
	else:
		log_data = [new_text] + old_log_arr

	# Write to log 
	log_file = 'greyhouse_status.log'
	with open(log_file, 'w') as out:
		out.write('# Previous responses (newest first)\n')
		out.write('\n'.join(log_data))

def hourly_tweet():
	'''Tweets every hour the "status" of seats'''
	tweets = get_responses()

	# Attempt to read history
	try:
		with open('greyhouse_status.log', 'r') as history:
			prev_tweets = [x.strip() for x in history.readlines()[1:]]
	except:
		prev_tweets = []

	now = datetime.now()
	# Exit if Greyhouse is closed
	if (now.hour > 22) or (now.hour < 7):
		print('Greyhouse is closed, and a closed message should have already been sent. Not sending tweet.')
		exit()

	# Post an opened message at 8am
	if now.hour == 8:
		possible_tweets = tweets['opened']
	# Post a closed message at 10pm
	elif now.hour == 22:
		possible_tweets = tweets['closed']
	# Normal tweet
	else:
		# Remove previous tweets from options
		possible_tweets = tweets['default']
		for item in prev_tweets:
			if item in possible_tweets: 
				possible_tweets.remove(item)
	
	# Tweet and log
	next_tweet = random.choice(possible_tweets)
	send_tweet(next_tweet)
	write_to_log(prev_tweets, next_tweet)

def retweet_from_last_minutes(user, mins):
	'''Retweets a random tweet from user in the past minutes'''
	api = get_connection()
	timeline = api.user_timeline(user, count=20)

	# Get only tweets that have been posted in the last hour
	recent_tweets = []
	hour_ago = datetime.now(tz=tz.tzlocal()) - timedelta(seconds=mins*60)
	for tweet in timeline:
		# Convert utc time to local
		tweet_time = tweet.created_at.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
		if tweet_time > hour_ago:
			recent_tweets.append(tweet)
	
	if recent_tweets:
		tweet = random.choice(recent_tweets)
		api.retweet(tweet.id)

if __name__ == '__main__':
	try:
		hourly_tweet()
	except Exception as ex:
		# Pushover alert if something goes wrong
		if use_pushover:
			timestr = time.strftime('%d/%m/%Y %H:%I %p')
			pushover.init(PUSHOVER_APP_TOKEN)
			pushover.Client(PUSHOVER_USER).send_message('Error:\n{}'.format(ex),
														title='{} error {}'.format(__file__, timestr))
		# Re-raise the exception for any logs
		raise ex
