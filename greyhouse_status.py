import random
import twitter
import datetime
try:
	from greyhouse_status_keys import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET
except ImportError:
	print('Could not get required keys from greyhouse_status_keys.py')

def send_tweet(text):
	'''Sends the text as a tweet'''
	api = twitter.Api(consumer_key=CONSUMER_KEY,
					  consumer_secret=CONSUMER_SECRET,
					  access_token_key=ACCESS_TOKEN_KEY,
					  access_token_secret=ACCESS_TOKEN_SECRET)
	try:
		status = api.PostUpdate(text)
		print('Tweet "{}" sent at {}'.format(next_response, status.created_at))
	except Exception as ex:
		print('Tweet could not be sent. Error below:\n{}'.format(ex))

def write_to_log(old_log_arr, new_text):
	# Only keep a limited amount of history in the log
	num_responses_stored = 3
	if len(old_log_arr) >= num_responses_stored:
		log_data = [new_text] + old_log_arr[0:(num_responses_stored-1)]
	else:
		log_data = [new_text] + old_log_arr

	# 
	with open('greyhouse_status.log', 'w') as out:
		out.write('# Last three responses (newest first)\n')
		out.write('\n'.join(log_data))

if __name__ == '__main__':
	# All possible responses to Tweet
	responses = [
		'No.',
		'Nope.',
		'Nah fam',
		'Lol nope',
		'Hell nah',
		'Hell no',
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
		'Nope, the same 20 people have been here for the past hour, probably are\'nt leaving soon',
		'If you\'re willing to throw elbows, tons!',
		'No seats available until 10pm!',
		'Current wait time: TBD',
	]

	closed_responses = [
		'Well there would be seats open, but we\'re closed',
	]

	# Attempt to read history
	try:
		with open('greyhouse_status.log', 'r') as history:
			prev_responses = [x.strip() for x in history.readlines()[1:]]
	except:
		prev_responses = []

	# Post a closed message at 10pm
	now = datetime.datetime.now()
	if now.hour == 20:
		next_response = random.choice(closed_responses)
		send_tweet(next_response)
		write_to_log(prev_responses, next_response)
	# Don't post again until 7am
	elif (now.hour > 20) or (now.hour < 7):
		print('Greyhouse is closed, and a closed message should have already been sent. Not sending tweet.')
	# Normal tweet
	else:
		# Remove previous responses from options
		for item in prev_responses:
			if item in responses:
				responses.remove(item)

		# Get the next reponse
		next_response = random.choice(responses)
		send_tweet(next_response)
		write_to_log(prev_responses, next_response)
