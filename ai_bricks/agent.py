from textwrap import dedent
import re

# 	Question: the input question you must answer
def v1(question, model, actions, hints='', iter_limit=5):
	out = {'text':''}
	print(f'QUESTION: {question}\n')
	prompt = f"""
	Answer the following questions as best you can.
	Question: {question}
	
	You are augmented with the following actions: {' '.join(actions)}.
	{hints}

	Use the following format:
	Thought: you should always think about what to do
	Action: the action to take, should be one of {' '.join(actions)}
	Action Input: the input to the action
	Observation: the result of the action
	... (this Thought/Action/Action Input/Observation can repeat N times)
	Thought: I now know the final answer
	Final Answer: the final answer to the original input question

	Begin!
	"""
	prompt = dedent(prompt)
	#print(prompt) # XXX
	for i in range(iter_limit):
		x = model.complete(prompt, stop=['Observation:'])
		#print()
		#print('>>> rtt',x['rtt'])
		#print('usage',x.get('usage',{}))
		steps = re.findall('(?m)^([A-Z][^:]+):\s*(.*?)(?:\n|$)', x['text'])
		for step in steps:
			print(step[0]+':',step[1])
			pass
		if not steps:
			out['text'] = x['text']
			out['status'] = 'Error: empty steps'
			break
		elif steps[-1][0] == 'Final Answer':
			out['text'] = x['text']
			out['status'] = 'ok'
			break
		elif steps[-2][0] == 'Action' and steps[-1][0] == 'Action Input':
			action = steps[-2][1].strip().partition(' ')[0]
			input0 = steps[-2][1].strip().partition(' ')[2] # workaround for not so smart models
			input  = steps[-1][1].strip() or input0
			if action[0]!="[":
				action = '['+action+']'
			if action not in actions:
				obs = f'Action "{action}" is not allowed. Allowed actions: {" ".join(actions)}.'
			else:
				obs = actions[action](input)
			prompt = prompt + x['text'].rstrip() + f'\nObservation: {str(obs).rstrip()}\n'
			print(f"Observation: {str(obs).rstrip()}") # XXX
			#print(prompt) # XXX
		else:
			out['status'] = f'Error: abnormal steps pattern - {steps}'
			break
	else:
		out['status'] = 'Error: iterations limit reached'
	print() # XXX
	return out
