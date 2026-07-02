BEHAVIOUR_DIMENSION_SUMMARIES = {
    'ADAPTABILITY': 'Assesses whether behaviour changes with context, feedback, obstacles, prior experience, or revised plans.',
    'HUMAN_IMPERFECTIONS': 'Assesses hesitation, forgetfulness, distraction, interruptions, and other imperfect human-like action flow.',
    'RECOVERY': 'Assesses mistake detection, correction, self-checking, and whether recovery looks natural or overly convenient.',
    'PREFERENCES_AND_NON_OPTIMALITY': 'Assesses preference-driven choices, adequate rather than optimal actions, and small routine variations.',
    'MICRO-BEHAVIOUR': 'Assesses automatic or subconscious behaviours with no outward task goal, such as fidgeting or yawning.',
    'ENVIRONMENTAL_CONTEXT': 'Assesses whether actions respond to objects, surroundings, and environmental constraints.',
    'PHYSIOLOGICAL_CONTEXT': 'Assesses whether actions are physically plausible and reflect realistic bodily constraints.',
    'ATTENTIVENESS': 'Assesses monitoring, attention shifts, selective awareness, and whether some information is overlooked.',
    'FORESIGHT': 'Assesses planning ahead, bundling related actions, postponing goals, and managing multiple goals.',
    'SOCIAL': 'Assesses adaptation, coordination, and awareness when other agents or living beings are present.'
}



BEHAVIOUR_CATEGORY_RUBRIC = {

    #INTENTIONALITY PROMPTS: intentionality of the agent's behaviour, including the presence of goals, plans, and motivations behind their actions.  Rank the intentionality on a scale from 10 (human) to 0 (generated)."
    #'INTENTIONALITY_PROMPTS' : [
    #    'Does the agent exhibit goal-directed behaviour?', #Does the behaviour build towards a larger goal? 
    #    'Does the behaviour show a hierarchy of short and long term goals?',
    #    'Do the inferred goals of the actions and tasks fit the scenario context?',
    #    'Are the agents actions coherent across time steps and do they remain so over time?'],   

    #ADAPTABILITY PROMPTS: adaptability of the agent's behaviour. Dealing with uncertainty, ability to improv, re-plan or update plans as they happen.
    'ADAPTABILITY' : [
		'Does the agent show evidence of adapting its behaviour when the environment or context changes?',
        'Does the agent suggest the use of prior experience when encountering familiar situations?',
        'Does the agent show evidence of adjusting its behaviour in response to external feedback?',
        'Does the agent revise its goals when encountering events that hinder its inferred task from its action sequence?',
        'Does the agent show evidence of flexibility in their behaviour, such as being able to switch between different strategies or approaches to achieve their goals?',
        #'Does the agent show evidence of improvisation or creativity in their actions?',   - similar to the above prompt              
		'Does the agent show evidence of re-planning or updating their plans as they happen?'
     ],

    #ROUTINE AND VARIABILITY PROMPTS: 
    ##'ROUTINE' : [
        # 'Does the agent show evidence of habitual or routinely executed actions?',   
    ##    'Does the agents behaviour show evidence of routine, automated actions and procedural familiarity with their tasks',                            
    ##    'Does the agents suggest procedural familiarity with the task?',
    ##    'If the agents actions are inferred as uncertain, does the agents behaviour suggest exploratory, investigative behaviour i.e. through trial and error?',
    ##    'Does the agent show an ability to perform routine tasks with a degree of variability, if the task is repeated can the agent complete it using different action sequences?',
    ##    'Do actions appear habitual or automatic rather than explicitly deliberative?'
    ##    'Does the agents actions contain actions that verify the progress state of the action?'
    ##],

    #IMPERFECTIONS, ERRORS, VARIABILITY
    'HUMAN_IMPERFECTIONS' : [  
        'Do the actions of the agent show uncertainty, such as hesitation, action reversal or changes of course in their carrying out of the task?',
        'Does the agent show signs of forgetfulness in their action sequences?',
        'Does the agent shows signs of distraction from the current task?',
        'Are there interruptions in behaviour and action flow, such as pauses between actions or interruptions in task flow (in contrast to a smooth flow)?'
    ],

    #ERROR RECOVERY 
    'RECOVERY' : [
        'If actions of the agent are inferred as mistakes, do the mistakes and recovery appear overly direct or artificially convenient? The more true this is, the lower the score.',
        'If the agent shows signs of mistakes, are the agents able to correct their path of action, or recover from a potential error?',
        'Does the agent show evidence of being able to detect and recognise its own mistakes?',
        'Does the behaviour show evidence of reviewing or self-checking between tasks and after mistakes?'
    ],


    #EMOTIONS
    ##'EMOTIONAL_ACTION_PROMPTS' : [
    ##    'Does the agent show behaviour and actions that are not purely rational or utility-maximising?'
    ##], #remove prompt - example model response is: 'agents behaviour shows some emotional action such as adding milk and removing the teabag


    #NON-OPTIMALITY 
    'PREFERENCES_AND_NON_OPTIMALITY' : [ #deviation from a clean task flow
        'Does the agents behaviour suggest preference-driven choices over optimal actions?',
        'Does the agent behaviour display sub-optimal behaviour?', 
        'Does the agents behaviour show signs of settling for adequate rather than optimal action flows?',
        'Does the agents behaviour show small variations in action sequences that can be inferred as routine behaviour?'
    ],
    
    #TIMING
    # 'TIMING' : [
    #     'Do the time intervals between each action/ different actions or task sequences performed show realistic variation? ',
    #     'Do the intervals between consecutive actions show human-like irregularity, including natural pauses, quicker automatic movements, and longer gaps before complex or context-dependent actions?',
    #     'Do the times taken for each action correspond with the time generally required for the actions?',
    #     'Are the times taken to perform tasks realistic rather than optimally efficient?'
    # ],

    #MICRO-BEHAVIOURS
    #'MICRO-BEHAVIOUR' : [
    #    'Does the agents behaviour perform any automatic, subconscious or micro-behaviours, behaviours with no outward goal? These are behaviours such as yawning, stretching, fidgeting, sighing, flinching, startling, hiccups etc.',
    #],

    #ENVIRONMENTAL CONTEXTUAL BEHAVIOUR
    'ENVIRONMENTAL_CONTEXT' : [
	    'Do the actions of the human adapt to the locations of the objects they are interacting with?',
	    'Do the agents actions show an awareness of their environmental constraints, surrounding wise?', #i.e. physically, walking around obstacles, repositioning objects, adjusting grip, changing posture
	    'Do the actions of the human show that they have been influenced by their surrounding environment?'
    ],

    #PHYSIOLOGICAL_CONTEXT
    'PHYSIOLOGICAL_CONTEXT' : [
	    'Do the agents actions show an awareness of and reflect realistic constraints of the body i.e. the likelihood of an action being able to be performed?',
	    'Do the agents actions and behaviour seem physically plausible?'
	],
	
    #ATTENTIVENESS
    'ATTENTIVENESS' : [
        'Does the agent exhibit actions that suggests it periodically monitor or reassess its environment?',
	    'Does attention shift between multiple goals or objects?',
	    'Does the agents behaviour suggest selective attention rather than perfect awareness of the environment?',
	    'Does the agents behaviour show signs that some information is overlooked?'
	],
    
    #FORESIGHT
    'FORESIGHT' : [
	    'Does the agent show signs of bundling related actions together when possible?',
	    'Does the behaviour indicate towards an awareness of anticipating future resource needs, or evidence of planning/ foresight for future tasks or actions?',
	    'Are multiple goals being pursued simultaneously?',
	    'Are some goals temporarily postponed or left in favour of other goals?'
	],
	
    #SOCIAL BEHAVIOUR
    'SOCIAL': [
        'If other agents or living beings are present, does the agents behaviour adapt to their actions?',
        'If other agents are present, does the agent coordinate its actions with the others?',
        'If other agents are present, does the agent show an adequate awareness of social expectations?'
    ]
}                              