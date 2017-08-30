import tweepy
import pushover
import random
import datetime
import time
import os

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
	'''Returns all "normal" responses, both text and media'''
	# Text responses
	responses = [
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
	]
	# Add media as responses
	# Get the path of this file, since running an exterior shell command will look in a different media folder
	media_folder = './media' #os.path.join(os.path.dirname(os.path.realpath(__file__)), 'media')
	responses += get_files_in_folder(media_folder)
	return responses

def get_files_in_folder(folder):
	'''Returns an array of filenames directly under folder'''
	return [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

def send_tweet(string):
	'''Sends a tweet with media if the string is a valid file path, sends the string as a tweet otherwise'''
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth)

	# Validate keys
	if not api.verify_credentials():
		raise IOError('Twitter API keys are invalid')
	
	# Send tweet
	try:
		if os.path.isfile(string):
			status = api.update_with_media(string)
		else:
			status = api.update_status(string)
		print('Tweet "{}" sent at {}'.format(string, status.created_at))
	except tweepy.TweepError as ex:
		if ex.message[0]['code'] != 187: # Duplicate status/tweet
			raise Exception('Tweet "{}" could not be sent. Error below:\n{}'.format(string, ex))

def write_to_log(old_log_arr, new_text):
	# Only keep a limited amount of history in the log
	num_responses_stored = 10
	if len(old_log_arr) >= num_responses_stored:
		log_data = [new_text] + old_log_arr[0:(num_responses_stored-1)]
	else:
		log_data = [new_text] + old_log_arr

	# Write to log 
	log_file = 'greyhouse_status.log'
	with open(log_file, 'w') as out:
		out.write('# Previous responses (newest first)\n')
		out.write('\n'.join(log_data))

if __name__ == '__main__':
	try:
		responses = get_responses()
		opened_responses = [
			'Just opened! Get \'em while they\'re hot!',
			'Open for business! Seats will be full in about 3 minutes.',
			'Hurry! We just opened so there\'s about 4 seats left!',
		]
		closed_responses = [
			'Well there would be seats open, but we\'re closed',
			'Closed. Rip',
			'Wait, every single chair is empty?! Oh we\'re closed',
		]

		# Attempt to read history
		try:
			with open('greyhouse_status.log', 'r') as history:
				prev_responses = [x.strip() for x in history.readlines()[1:]]
		except:
			prev_responses = []

		now = datetime.datetime.now()
		# Exit if Greyhouse is closed
		if (now.hour > 22) or (now.hour < 7):
			print('Greyhouse is closed, and a closed message should have already been sent. Not sending tweet.')
			exit()

		# Post an opened message at 7am
		if now.hour == 7:
			next_response = random.choice(opened_responses)
		# Post a closed message at 10pm
		elif now.hour == 22:
			next_response = random.choice(closed_responses)
		# Normal tweet
		else:
			# Remove previous responses from options
			for item in prev_responses:
				if item in responses:
					responses.remove(item)
			next_response = random.choice(responses)
		
		# Tweet and log
		send_tweet(next_response)
		write_to_log(prev_responses, next_response)
	except Exception as ex:
		# Pushover alert if something goes wrong
		if use_pushover:
			timestr = time.strftime('%d/%m/%Y %H:%I %p')
			pushover.init(PUSHOVER_APP_TOKEN)
			pushover.Client(PUSHOVER_USER).send_message('Error:\n{}'.format(ex),
														title='greyhouse_status.py error {}'.format(timestr))
		# Re-raise the exception for any logs
		raise ex
