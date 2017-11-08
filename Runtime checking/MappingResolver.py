def regex_resolver(msg):
	philosopher_id = msg[msg.find('[')+1:msg.find(']')]
	msg = msg.split('.')
	if '.' in msg:
		fork_id,msg = msg.split('.')

	if (msg == 'sitdown'):
		return philosopher_id+'.sitRequestAccepted'
	if (msg == 'eat'):
		return philosopher_id+'_'+philosopher_id+'.startedEating'
	if (msg == 'arise'):
		return philosopher_id+'.arise'
	if (msg == 'get'):
		return philosopher_id+'_'+fork_id+'.forkAccepted'
	if (msg == 'put'):
		return philosopher_id+'_'+fork_id+'.putFork'
	