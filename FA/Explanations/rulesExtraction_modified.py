import re
from itertools import cycle
import subprocess
import random
import csv
from Explanations import beliefs_tracing as bt

def AnswerSetFinder(Expression, AnswerSetFile):
    # find literals in the Answer Set totally, partially or not grounded
    # INPUTS: Expression -> partially/totally/non-grounded literal in string format
    #         AnswerSetFile -> the file containing the Answer Set obtaioned from SPARC
    # OUTPUT: list of matched grounded terms retrieved from the Answer Set
    #print('expr1', Expression)
    if "next" in Expression:
    	Expressions = re.split(r',(?![^(]*\))', Expression)
    else:
    	Expressions = [Expression]
    literal = []
    #print('Expressions', Expressions)
    for i in range(len(Expressions)):
    	Expression = Expressions[i]
    	
    	if not re.search('[\>\<\=\!]',Expression):
        	#print('here..................')
        	Expression = re.sub('\(', '\(', Expression)
        	Expression = re.sub('\)', '\)', Expression)
        	#Expression = re.sub('[0-9]', '[a-z0-9_]+(?:\(.+?\))?', Expression)
        	Expression = re.sub('[A-Z][0-9]?', '[a-z0-9_]+(?:\(.+?\))?', Expression)
        	#print('expr: ', Expression)
        	literal.append(re.findall("(?<!-)"+Expression, AnswerSetFile))

        	#print(literal)
    	else:
        	literal = [Expression]
    if [] not in literal and len(literal) > 1:
    	#print('non-empty literal')
    	found = 0
    	for match1 in literal[0]:
    	     if not found:
    	     	matches1 = re.findall(r'\d+,\d+\)', match1)
    	     	for match2 in literal[1]:
    	     		matches2 = re.findall(r'(?<=\d,)\d+,\d+\)', match2)
    	     		if matches1 == matches2:
    	     			#print('found', match1, match2)
    	     			found = 1
    	     			break
    	     elif found:
    	     	break
    	     	

    	if found:
    		literal = [match1+','+match2]
    	else:
    		literal = []
    	#print('chck', literal)
    elif [] in literal:
    	literal = []
    else:
    	literal = literal[0]
    #print('len', len(literal))
    #print('here------------------------', literal)
    return literal


def AxiomsFinder(Literal, ASPfile, option): #modified successfully
    # retrieve axioms in the ASP program that contains a given Literal in its head or body
    # INPUTS: Literal -> partially/totally/non-grounded literal in string format
    #         ASPfile -> the file containing the ASP program
    #         option  -> 'head' or 'body'. Indicates the part of the axiom looking for 
    # OUTPUT: list of matched rules retrieved from the ASP program
    #print('printing literal: ', Literal)
    #print('example: ',re.sub('([a-zA-Z0-9_]+)(?![a-zA-Z0-9_]*\()', ' [A-Z]+\\+?[0-9]?', 'occurs(pickup(rob1,blue_block),0)'))
    #occurs(pickup( [A-Z]+\+?[0-9]?, [A-Z]+\+?[0-9]?), [A-Z]+\+?[0-9]?)
    #occurs(move(learner,6,14),4)
    Literal = re.sub('([a-zA-Z0-9_]+)(?![a-zA-Z0-9_]*\()', '[A-Z]+\\+?[0-9]?', Literal)


    #print('L', Literal)
    Literal = re.sub('\(', '\(', Literal)
    Literal = re.sub('\)', '\)', Literal)
    #print(Literal)
    if option == 'head':
        axiom = re.findall(".*?"+"(?<!-)"+Literal+" :-.*?\.", ASPfile)
    else:
        axiom = re.findall(".*:-.*"+"(?<!-)"+Literal+".*\.", ASPfile)
    #print('GGGGGGGGGGGGGGGGGG')    
    #print('A', axiom)
    return axiom    


def Grounder(axiom, grounded_literal, option):
    # partially/totally ground literals in an axiom based on the ground of other literals from the same axiom
    # INPUTS: axiom            -> the axiom in string format
    #         grounded_literal -> one grounded term in string format
    #         option           -> 'head' or 'body'. Selects the part of the axiom to retrieve 
    # OUTPUT: list of partially/totally grounded terms
    grounds = re.findall('([a-zA-Z0-9_]+)(?![a-zA-Z0-9_]*\()',grounded_literal)
    #print('axiom', axiom)
    #print('gliteral', grounded_literal)
    nonground_finder = re.sub('\(', '\(', grounded_literal)
    nonground_finder = re.sub('\)', '\)', nonground_finder)
    nonground_finder = re.sub('([a-zA-Z0-9_]+)(?![a-zA-Z0-9_]*\\\\\()', '([a-zA-Z0-9_\+]+)(?![a-zA-Z0-9_]*\()', nonground_finder)
    #print('ngfinder', nonground_finder)
    variables = re.findall(nonground_finder, axiom)
    #print('hhhh', variables)
    for idx, variable in enumerate(variables[0]):
        axiom = re.sub(variable+'(?![a-zA-Z0-9])', grounds[idx], axiom)
    #print('axiomsub1', axiom)
    if option == 'body':
        axiom = re.findall("(?<=:-)(.*?)\.", axiom)
    else:
        axiom = re.findall("(.*)(?=:-)", axiom)
    axiom = re.sub(' ','',axiom[0])
    #print('axiom part', axiom)
    axiom = [re.sub('\.','',x) for x in re.split(':-|,(?= *[a-zA-Z#0-9_]+?[\(\=\<\>\!])',axiom)]# if not x.startswith('#')]
    #print('axiom', axiom)
    return axiom

def Grounding(axiom, grounded_literal):
    # INPUTS: axiom            -> the axiom in string format
    #         grounded_literal -> one grounded term in string format
    # OUTPUT: two lists containing variables and correspondents grounds
    grounds = re.findall('([a-zA-Z0-9_]+)(?![a-zA-Z0-9_]*\()',grounded_literal)
    nonground_finder = re.sub('\(', '\(', grounded_literal)
    nonground_finder = re.sub('\)', '\)', nonground_finder)
    nonground_finder = re.sub('([a-zA-Z0-9_]+)(?![a-zA-Z0-9_]*\\\\\()', '([a-zA-Z0-9_\+]+)(?![a-zA-Z0-9_]*\()', nonground_finder)
    variables = re.findall(nonground_finder, axiom)
    return list(variables[0]), grounds

def validateBody(groundTerms, rule):
    #test if the body of a rule holds based on the set of grounded terms from the answer set
    # INPUTS: groundTerms -> a simple list (or string) of grounded terms
    #         rule        -> the axiom in string format
    # OUTPUTS: 'True' or 'False', which means that a body holds or not
    if not isinstance(groundTerms, list):
        groundTerms = [groundTerms]

    if len(groundTerms) > 1:
        variables = []
        grounds = []
        for term in groundTerms:
            variable, ground = Grounding(rule, term)
            if re.search('[\=\<\>\!]+', term)!=None:
                variab = re.findall('[A-Z]+[a-z0-9]*', term)
                if all([v in variables for v in variab]):
                    equation = term
                    for v in variab:
                        equation = re.sub(v, grounds[variables.index(v)], equation)
                    if not eval(equation):
                        return False
            else:
              for ind, var in enumerate(variable):
                if var in variables:
                    if ground[ind]!=grounds[variables.index(var)]:
                        return False
                else:
                    variables.append(var)
                    grounds.append(ground[ind]) 
            

    terms = re.split(':-|,(?= *[a-z#A-Z0-9 _]+?[\(\=\<\>\!])',rule)
    terms = [re.sub(' ','\n?',re.sub('\(','\(',re.sub('\)','\)',term))) for term in terms[1:]]
    terms = [re.sub('[A-Z][0-9]?', '[a-z0-9_]+(?:\(.+?\))?', re.sub('\.','',term)) for term in terms if not re.search('not|[\>\<\=\!]',term)]
    #print(terms)
    #print([[re.search(term, groundTerm)!=None for groundTerm in groundTerms] for term in terms])
    return all([any([re.match(term, groundTerm)!=None for groundTerm in groundTerms]) for term in terms if not (re.search('[\>\<\=\!]',term) or term.startswith('not'))])


def planDescription(AnswerSet):
    # retrieves planned actions from an Answer set in chronological order
    actions = AnswerSetFinder('occurs(A,I)', AnswerSet)
    #sorting the actions by time-step
    order = [int(re.findall(',([0-9]+)',x)[-1]) for x in actions]
    sorted_actions = [action for _,action in sorted(zip(order,actions))]
    print('****** Plan description **********')
    print(sorted_actions)
    return sorted_actions


def whyAction(AnswerSet, ASPprogram, timestep,i):
    sorted_actions = planDescription(AnswerSet)
    if sorted_actions == []:
    	return [],[]
    action = sorted_actions[i]
    action_query = action
    action = re.sub(" ","",action)
    action = re.sub("\(","\(",action)
    action = re.sub("\)","\)",action)
    print('printing action: ', action)
    #action_query = [act for act in sorted_actions if re.search(action,act)!=None and re.search(','+timestep,act)!=None][0]
    
    '''
    action_query = []
    for act in sorted_actions:
        print('action matching',re.search(action, act))
        print(act)
        print(re.search('\),' + timestep, act))
        if re.search(action, act) is not None and re.search(',' + timestep, act) is not None:
            action_query.append(act)
            print('appending',act)
    '''
    #print("Matching actions:", action_query)


    timestep_query = re.findall(',([0-9]+)', action)
    #print('tsq',timestep_query)
    #print('aaction query: ', action_query)
    exec_conds = [AxiomsFinder('-'+act, ASPprogram, 'head') for act in sorted_actions[sorted_actions.index(action_query)+1:]] 
    #print('exec conds1: ', exec_conds)
    exec_conds = [[Grounder(exe, sorted_actions[sorted_actions.index(action_query)+1:][ind],'body') for exe in exec_cond] for ind, exec_cond in enumerate(exec_conds)]
    #print('exec_conds1', exec_conds)
    
    exec_conds = [[item for x in exec_cond for item in x] for exec_cond in exec_conds]
    #print('exec_conds2', exec_conds)
    
    #exec_conds_init = [[re.sub(',([0-9]+)', ','+str(timestep_query[-1]), x) for x in exec_cond] for exec_cond in exec_conds]
    exec_conds_init = [[re.sub(r',(\d+)\)(?![,\d])', ','+str(timestep_query[-1])+')', x) for x in exec_cond]for exec_cond in exec_conds]
    exec_conds_init = [[re.sub(r',(\d+)\)(?=(?:,-|,[a-zA-Z]))', ','+str(timestep_query[-1])+')', x) for x in exec_cond]for exec_cond in exec_conds_init]
    #print('exec_init', exec_conds_init)
    # select only the conditions actually changed in the next timestep1
    #exec_conds = [[re.sub(',([0-9]+)', ','+str(int(timestep_query[-1])+1), x) for x in exec_cond] for exec_cond in exec_conds]
    #exec_conds = [[re.sub(r',(\d+)\)(?![,\d])', ','+str(int(timestep_query[-1])+1)+')', x) for x in exec_cond]for exec_cond in exec_conds]
    #exec_conds = [[re.sub(r',(\d+)\)(?=(?:,-|,[a-zA-Z]))', ','+str(int(timestep_query[-1])+1)+')', x) for x in exec_cond]for exec_cond in exec_conds]
    #print('exec conds0: ', exec_conds)
    #exec_conds = [[[AnswerSetFinder(x, AnswerSet), indout + int(timestep_query[-1]+1)] for indin, x in enumerate(exec_cond) if AnswerSetFinder(x, AnswerSet)!=[] and AnswerSetFinder(exec_conds[indout][indin], AnswerSet)==[]] for indout, exec_cond in enumerate(exec_conds_init)]
    #exec_conds = [[[AnswerSetFinder(x, AnswerSet), indout + int(timestep_query[-1]) + 1] for indin, x in enumerate(exec_cond) if AnswerSetFinder(x, AnswerSet)!=[] and AnswerSetFinder(exec_conds[indout][indin], AnswerSet)==[]] for indout, exec_cond in enumerate(exec_conds_init)]
    #exec_conds = exec_conds1
    exec_conds1 = []

    for indout, exec_cond in enumerate(exec_conds_init):
    	inner_list = []
    	for indin, x in enumerate(exec_cond):
    		#print('out', indout, 'in', indin)
    		#print('shape', len(exec_conds))
    		#print('1 ', x, '2 ', exec_conds[indout][indin])
    		#if AnswerSetFinder(x, AnswerSet) != []:
    			#print('!!!!!!!!!!!asf of ', x, ' is', AnswerSetFinder(x, AnswerSet))
    		#if AnswerSetFinder(exec_conds[indout][indin], AnswerSet) == []:
    			#print('#########asf of ', exec_conds[indout][indin], ' is', AnswerSetFinder(exec_conds[indout][indin], AnswerSet))
    		for ind, y in enumerate(exec_conds):
    			for i, a in enumerate(y):
    				
    				if AnswerSetFinder(x, AnswerSet) != [] and AnswerSetFinder(a, AnswerSet) == []:
    					#print('~~~~~~~~~~here')
    					#print('asf x', AnswerSetFinder(x, AnswerSet), 'a', a)
    					#print('asf x', AnswerSetFinder(x, AnswerSet), 'a', a)
    					matches1 = re.findall(r'(\d+,\d+)\)', a)
    					#print('m1', matches1)
    					matches2 = re.findall(r'\((\d+,\d+),', AnswerSetFinder(x, AnswerSet)[0])
    					#print('m2', matches2)
    					if matches1 == matches2 and 'X2' not in a:
    						inner_list.append([AnswerSetFinder(x, AnswerSet),a, int(re.findall(',([0-9]+)',a)[-1])])
    						#print('Adding: ', [AnswerSetFinder(x, AnswerSet),a, int(re.findall(',([0-9]+)',a)[-1])])
    			#timestep = indout + int(timestep_query[-1]) + 1
    			#inner_list.append([x, timestep])
    	exec_conds1.append(inner_list)
    #print('exec conds2: ', exec_conds1)
    exec_conds = exec_conds1


    #exec_conds = exec_conds1
    #print('exec conds3: ', exec_conds)
    exec_conds = [item for cond in exec_conds for item in cond if cond!=[]]
    order = [x[2] for x in exec_conds]
    sorted_conds = [action for _,action in sorted(zip(order,exec_conds))]
    if len(sorted_conds) != 0:
    	explanation = sorted_conds[-1]
    else:
    	return sorted_actions, []
    #print('len',len(explanation))
    #print('EXPL',explanation)
    #explanation = [explanation[0][0], sorted_actions[explanation[1]]]
    print("Why", sorted_actions[i],"?")
    if i+1 < len(sorted_actions):
    	next_action = sorted_actions[i+1]
    else:
    	next_action = []
    print(explanation, next_action)
    return sorted_actions, explanation


def whyNotAction(AnswerSet, ASPprogram, action, timestep='1'):
    action = re.sub(" ","",action)
    action_query = "occurs("+re.findall('([a-z]+?\([a-zA-z0-9_,]+?\))', action)[0]+","+timestep+")"
    timestep_query = eval(timestep)
    exec_conds = AxiomsFinder('-'+action_query, ASPprogram, 'head')
    exec_conds = [Grounder(exe, action_query,'body') for exe in exec_conds] 
    exec_conds = [item for x in exec_conds for item in x]
    exec_conds = [AnswerSetFinder(x, AnswerSet) for x in exec_conds]
    #exec_conds = [item for cond in exec_conds for item in cond if cond!=[] and not item.startswith('#')]
    #exec_conds = [exec_cond for exec_cond in exec_conds if 'holds' in exec_cond or 'has_' in exec_cond]
    
    explanation = [exec_conds]
    print('Why Not?')
    print(explanation)
    return explanation


def whyBelief(AnswerSet, ASPprogram, belief, timestep=""):
    axiom = belief
    while axiom!=[]:
        explanation = axiom
        axioms = [[AxiomsFinder(ax, ASPprogram, 'head') for ax in axio][0] for axio in axiom]
        state_constr = [[Grounder(ax, axiom[ind][0],'body') for ax in axi] for ind, axi in enumerate(axioms)]
        state_constr = [item for x in state_constr for item in x]
        state_constr = [[AnswerSetFinder(x, AnswerSet) for x in state_cons] for state_cons in state_constr]
        state_constr = [[x for x in state if not (x==[] and len(state)>1)] for state in state_constr]
        comb = []
        for state in state_constr:
            if len(state)<2:
                comb.append(state)
            if len(state)==2:
                comb.append([[x,y] for x in state[0] for y in state[1]])
            if len(state)==3:
                comb.append([[x,y,z] for x in state[0] for y in state[1] for z in state[2]])
        rules = [item for x in axioms for item in x] #These are the reshaped axioms for being used to body validation
        state_constr = [[st for st in state if validateBody(st, rules[ind])] for ind, state in enumerate(comb)] 
        state_constr = [state[0] for state in state_constr if state!=[]]     
        axiom = [[item] for x in state_constr for item in x]
    print(explanation)
    return explanation
    

def getact():
	agent = ['learner']
	guard = ['guard2', 'guard3']
	attacker = ['attacker1', 'attacker2', 'attacker3']
	other_agents = guard + attacker
	all_agents = agent + other_agents
	x_value = list(range(20))  # 0 to 19
	y_value = list(range(16))  # 0 to 15
	value = list(range(11))  # 0 to 10
	sum_val = list(range(51))  # 0 to 50
	direction = ['north', 'south', 'east', 'west', 'north_east', 'north_west', 'south_east', 'south_west',
             'north1', 'south1', 'east1', 'west1', 'north_east1', 'north_west1', 'south_east1', 'south_west1',
             'north2', 'south2', 'east2', 'west2', 'north_east2', 'north_west2', 'south_east2', 'south_west2']
	step = list(range(21))  # 0 to n
	boolean = ['true', 'false']
	# Actions
	acts = ['move', 'shoot', 'rotate']#leave out rotate?
	agent_actions = ['move(' + agent[0] + ',' + str(x) + ',' + str(y) + ')' for x in x_value for y in y_value]
	rotate_actions = ['rotate(' + agent[0] + ',' + direction + ')' for direction in direction]
	shoot_actions = ['shoot(' + agent[0] + ',' + attacker + ')' for attacker in attacker]
	Actions = agent_actions+rotate_actions+shoot_actions
	action = random.choice(acts)
	selected = []
	for a in Actions:
		if action in a:
			selected.append(a)
	#print(action)
	action = random.choice(selected)
	return action


def compare(AS1, AS2, ASP1, ASP2):
	
	#reading the files
	t = open(ASP1,"r")
	ASP1 = t.read()
	t.close()
	#openning ASP file
	f = open(AS1,"r")
	AS1 = f.read()
	f.close()
	t = open(ASP2,"r")
	ASP2 = t.read()
	t.close()
	#openning ASP file
	f = open(AS2,"r")
	AS = f.readlines()
	f.close()
	
	#change AS2 file
	for action in AS2:
                	if 'shoot' in action:
                			killed = re.findall("attacker[0-9]",action)[0]
                			time_killed = re.findall(",([0-9]+)",action)[-1]
                			shoot_goal = True
                	if 'shoot' in action:
                		for i in range(len(AS)):
                			bel = AS[i]
                			if 'shot' in bel and re.findall("[0-9]",bel)[-1] > time_killed and '-' not in bel:
                				answer_list[i] = '-'+bel
                				#print('changing ', bel, 'to ', answer_list[i])
        
	actions = planDescription(AS1)
	with open(AS2, 'w') as f:
        	for bel in AS:
        		f.write(f"{bel}\n")
	correct = 0
	tot = 0
	for time in range(len(actions)):
		#get different action
		act = 'occurs('+getact()+','+str(time+1)+')'
		while act == actions[time]:
			act = 'occurs('+getact()+','+str(time+1)+')'
		tot += 1
		print('act', act)
		print(whyNotAction(AS1, ASP1, act, str(time+1)), str(time+1))
		print(whyNotAction(AS2, ASP2, act, str(time+1)), str(time+1))
		if whyNotAction(AS1, ASP1, act, str(time+1)) == whyNotAction(AS1, ASP1, act, str(time+1)):
			correct += 1
	accuracy = float(correct / tot) * 100.0
	return accuracy
	

def explain(AS1, ASP, step, length, j):
	
	#reading the files
	file_names = [AS1, "Explanations/next_dir", "Explanations/next_to_terms.txt", "Explanations/not_next"]
	#file_names2 = ["history2", "Explanations/next_to_terms.txt", "Explanations/not_next","Explanations/next_dir"]
	AnswerSet = ""
	# Iterate through the file names and read their contents
	for file_name in file_names:
    		with open(file_name, "r") as file:
        		file_content = file.read()
        		AnswerSet += file_content
        
	 
	t = open(ASP,"r")
	ASP = t.read()
	t.close()
	#openning ASP file
	AS = AnswerSet
	#print('AS', AS[-5:])
	#f = open(AS,"r")
	#AS = f.read()
	#f.close()
	#planDescription(AS)
	explanation1 = []
	explanation2 = []
	actions = []
	i = 0
	for stp in range(step, step+length):
		print('time step', stp)
		plan, explanation_1 = whyAction(AS, ASP, str(stp),i)
		explanation1.append(explanation_1)
		'''
		if 'holds(shot(attacker1),'+str(stp)+')' in AS:
			action = 'shoot(learner,attacker1)'
		if 'holds(shot(attacker2),'+str(stp)+')' in AS:
			action = 'shoot(learner,attacker2)'
		if 'holds(shot(attacker3),'+str(stp)+')' in AS:
			action = 'shoot(learner,attacker3)'
		else:
			action = getact()
		'''
		action = getact()
		print("Why Not", action,"?")
		actions.append(action)
		#action = input("Enter an action A to ask the system why not A?")
		explanation2 += whyNotAction(AS, ASP, action, str(stp))
		i += 1
		occur = '-occurs('+action+','+str(stp)+')'
		
		
		tr = bt.get_tree(file_names,occur)
		data = [j, plan, explanation1, actions, explanation2, tr]
		with open('explanations.csv', 'a', encoding='UTF8') as f:
			writer = csv.writer(f)
			writer.writerow(data)
		
		
	
######## OPENNING REQUIRED FILE: Answer Set and ASP program #####
'''
answer = subprocess.check_output('java -jar sparc.jar learner.sp -A',shell=True)
#answerSet_file = open('answer_set', 'w')
answer_split = (answer.decode('ascii'))
with open("answer_set", "w") as asf:
       asf.write(answer_split + '\n')
''
asp_learner = 'learner.sp'
asp = '\n'.join(answer_split)
f1 = open(asp_learner, 'w')
#print('obs', obs)
#print('asp_split',asp_split)
f1.write(asp)
f1.close()


#openning Answer set file
t = open('learner.sp',"r")
ASPprogram = t.read()
t.close()
#openning ASP file
f = open('history',"r")
AnswerSet = f.read()
f.close()

t = open('learner.sp',"r")
ASPprogram = t.read()
t.close()
t = open('without.sp',"r")
ASPprogram2 = t.read()
t.close()
file_names = ["history", "next_to_terms.txt", "not_next","next_dir"]
AnswerSet = ""
# Iterate through the file names and read their contents
for file_name in file_names:
    with open(file_name, "r") as file:
        file_content = file.read()
        AnswerSet += file_content
 
file_names = ["history2", "next_to_terms.txt", "not_next","next_dir"]
AnswerSet2 = ""
# Iterate through the file names and read their contents
for file_name in file_names:
    with open(file_name, "r") as file:
        file_content = file.read()
        AnswerSet += file_content
#################################################################
#planDescription(AnswerSet)
explanation = whyNotAction(AnswerSet, ASPprogram, 'shoot(learner,attacker3)', timestep = '9')
print('wthout')
explanation = whyNotAction(AnswerSet2, ASPprogram2, 'shoot(learner,attacker3)', timestep = '9')

#explanation = whyAction(AnswerSet, ASPprogram, timestep="8")

#belief = whyBelief(AnswerSet, ASPprogram, [['-holds(agent_shot(attacker3),1)']])#,['-holds(stable(book3),0)']])
'''
