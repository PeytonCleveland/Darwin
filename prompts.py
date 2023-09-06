EQUAL_PROMPT="""Here are two Instructions to ChatGPT, do you think they are equal to each other? Equal prompts
meet the following requirements:

1. They have same constraints and requirments.
2. They have same depth and breadth of the inquiry.
3. They have interchanged words or are rephrased but don't have meaningful differences otherwise

The First Prompt: {first}
The Second Prompt: {second}
Your Judgement (Just answer: Equal or Not Equal. No need to explain the reason.):"""

SYSTEM_PROMPTS=[
    # 1
    """You are Ocelot, a large language model trained by Digital University, based on the Llama 2 architecture. 
    You are helpful, respectful, and honest. Always answer as helpfully as possible, while being safe. If a 
    question does not make sense, or is not factually coherent, explain why instead of answering with something
    not correct. Your training cutoff date is 2023-07. The current date is {date}.""",
    # 2
    """You are a helpful assistant. Respond truthfully and think through your instructions step-by-step.""",
    # 3
    """You are an AI assistant that helps people find information. User will you give you a question. Your task
    is to answer as faithfully as you can. While answering think step-bystep and justify your answer."""
]

DEPTH_EVOLUTION_PROMPTS=[
    # 1. Deepening
    """I want you act as a Prompt Rewriter. Your objective is to rewrite a given prompt into a more complex version
    to train future language models on realistic, complext tasks. The rewritten prompt must be reasonable, must sound
    like it's written by a curious user and must be understandable. Do not simply reword the existing prompt. Rather,
    add depth by introducing more layers or aspects to the subject Your rewriting cannot omit any table or code in
    #Given Prompt#, they must be retained. You SHOULD complicate the given prompt using the following method: If
    #Given Prompt# contains inquiries about certain issues, the depth and breadth of the inquiry can be increased.
    ‘given prompt’ and ‘rewritten prompt’ are not allowed to appear in #Rewritten Prompt#, only respond with the
    rewritten prompt.
    #Given Prompt#:
    {prompt}
    #Rewritten Prompt#:""",

    # 2. Concretizing
    """I want you act as a Prompt Rewriter. Your objective is to rewrite a given prompt into a more complex version
    to train future language models on realistic, complex tasks. The rewritten prompt must be reasonable, must sound
    like it's written by a curious user and must be understandable. Do not simply reword the existing prompt. Rather,
    add depth by making the prompt more specific. Your rewriting cannot omit any table or code in #Given Prompt#, they
    must be retained. You SHOULD complicate the given prompt using the following method: Please replace general concepts
    with more specific concepts. ‘given prompt’ and ‘rewritten prompt’ are not allowed to appear in #Rewritten Prompt#,
    only respond with the rewritten prompt.
    #Given Prompt#:
    {prompt}
    #Rewritten Prompt#:""",

    # 3. Increasing Reasoning
    """I want you to act as a Prompt Rewriter. Your objective is to rewrite a given prompt to require more detailed reasoning 
    and thoughtful answers from future language models. The rewritten prompt must be reasonable, must sound like it's written
    by a curious user and must be understandable. Do not simply reword the existing prompt. Rather, add depth by asking for
    more in-depth reaasoning or requiring multiple steps of thought. Your rewriting cannot omit any table or code in 
    #Given Prompt#, they must be retained. You SHOULD complicate the given prompt by asking for more in-depth reasoning or
    requiring multiple steps of thought. ‘given prompt’ and ‘rewritten prompt’ are not allowed to appear in #Rewritten Prompt#,
    only respond with the rewritten prompt.
    #Given Prompt#:
    {prompt}
    #Rewritten Prompt#:""",
    
    # 4. Complicating Input
    """I want you to act as a Prompt Rewriter. Imagine you are crafting a question that demands more intellectual engagement.
    The rewritten prompt must be reasonable, must sound like it's written by a curious user, and be understandable. Do not simply
    reword the existing prompt. Rather, add depth by complicating the input and adding new complexities and constraints. Your
    rewriting cannot omit any table or code in #Given Prompt#, they must be retained. You SHOULD complicate the given prompt by
    adding new complexities and constraints. ‘given prompt’ and ‘rewritten prompt’ are not allowed to appear in #Rewritten Prompt#.
    Only respond with the rewritten prompt.
    #Given Prompt#:
    {prompt}
    #Rewritten Prompt#:"""
]

DIFFICULTY_PROMPT="""We would like you to evaluate and rate the difficulty and complexity of the following prompt. You
should give an overall score on a scale of 1 to 10, where a higher score indicates higher difficulty and
complexity. You must just give a score without any other reasons.
## Prompt:
{prompt}
## Score:"""

BREADTH_EVOLUTION_PROMPT="""I want you to act as a Prompt Creator. Your goal is to draw inspiration from the #Given Prompt#
to create a brand new prompt. This new prompt should belong to the same domain as the #Given Prompt# but be even more unique. 
The LENGTH and difficulty level of the #Created Prompt# should be similar to that of the #Given Prompt#. The #Created Prompt#
must be reasonable, must sound like it's written by a curious user and must be understood and responded to by humans. ‘given prompt’
and ‘created prompt’ are not allowed to appear in #Created Prompt#.
#Given Prompt#:
{prompt}
#Created Prompt#:"""