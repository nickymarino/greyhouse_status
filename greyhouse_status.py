import random

try:
    import greyhouse_status_keys
except ImportError:
    print('greyhouse_status_keys.py not found')
    exit()

if __name__ == '__main__':
    # All possible responses to Tweet
    responses = ['No',
                'Nope',
                'Don\'t even bother',
                'Wait there\'s one! \n...Oh someone just sat down',
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
    print(next_response)

    # Only keep a limited amount of history in the log
    if len(prev_responses) >= 3:
        log_data = [next_response] + prev_responses[:-1]
    else:
        log_data = [next_response] + prev_responses

    # 
    with open('greyhouse_status.log', 'w') as out:
        out.write('# Last three responses (newest first)\n')
        out.write('\n'.join([]))
