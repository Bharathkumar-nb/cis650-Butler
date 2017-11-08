def mapping(msg): #phil[0].a.get # phil[0].sitdown
	philosopher_id = msg[msg.find('[')+1:msg.find(']')]
	msg = msg.split('.')[1:]
	if len(msg) == 2:
		fork_id,msg = msg

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
	return ''
	
def reverse_mapping(msg): #1.sitReqAcc #1_a.forkAcc #1_1.startEat
	philosopher_id,msg = msg.split('.')
	if '_' in philosopher_id:
		philosopher_id,fork_id = msg.split('_')

	if (msg == 'sitRequestAccepted'):
		return 'phil['+philosopher_id+'].sitdown'
	if (msg == 'startedEating'):
		return 'phil['+philosopher_id+'].eat'
	if (msg == 'arise'):
		return 'phil['+philosopher_id+'].arise'
	if (msg == 'forkAccepted'):
		return 'phil['+philosopher_id+'].'+fork_id+'.get'
	if (msg == 'putFork'):
		return 'phil['+philosopher_id+'].'+fork_id+'.put'
	return ''
	