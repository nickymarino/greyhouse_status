import random
import twitter
try:
    from greyhouse_status_keys import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET
except ImportError:
    print('Could not get required keys from greyhouse_status_keys.py')

if __name__ == '__main__':
    # All possible responses to Tweet
    responses = ['No.',
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
    ]

    # Attempt to read history
    try:
        with open('greyhouse_status.log', 'r') as history:
            prev_responses = [x.strip() for x in history.readlines()[1:]]
    except:
        prev_responses = []
    
    # Remove previous responses from options
    for item in prev_responses:
        if item in responses:
            responses.remove(item)

    # Get the next reponse
    next_response = random.choice(responses)
    
    # Send tweet
    api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=ACCESS_TOKEN_KEY,
                      access_token_secret=ACCESS_TOKEN_SECRET)
    try:
        status = api.PostUpdate(next_response)
        print('Tweet "{}" sent at {}'.format(next_response, status.created_at))
    except Exception as ex:
        print('Tweet could not be sent. Error below:\n{}'.format(ex))

    # Only keep a limited amount of history in the log
    num_responses_stored = 3
    if len(prev_responses) >= num_responses_stored:
        log_data = [next_response] + prev_responses[0:(num_responses_stored-1)]
    else:
        log_data = [next_response] + prev_responses

    # 
    with open('greyhouse_status.log', 'w') as out:
        out.write('# Last three responses (newest first)\n')
        out.write('\n'.join(log_data))
