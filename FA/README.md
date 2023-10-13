# Knowledge based Ad hoc Teamwork

## Folder structure

```bash
.
├── ASP                     # ASP source files for the ad hoc agent
├── gym_fortattack          # Fort Attack domain implementation files
├── malib                   # Configuration files
├── models                  # Models of other agents
├── multiagent              # Fort Attack domain implementation files
├── action_policy.py        # Set action policies for other agents
├── ad_hoc_mod.py           # Ad hoc agent implementation modified to incorporate explanation and learning
├── arguments.py            # Default argument setup
├── fortattack.py           # Main source file
├── policies.py             # Policies for other agents
├── axioms_learn.py         # Relational RL and decision tree induction implementation
├── rulesExtraction_modified.py # Methods to form answers from the answer set to user queries
└── beliefs_tracing.py      # Methods to form belief trees for an episode
```

explanations.csv contains examples of answers to randomly generated questions and a belief tree for 40 ad hoc agent calls.
pre_without.sp is the ASP program without a causal law, while pre_with.sp is the normal ASP program.

## Installation
Create an anaconda environment with python 3.6 using the following command (Note: this code has only been tested on Linux with Python 3.6):

```setup
conda create -n fortattack python=3.6 pip
```

Activate the environment and install the required packages by executing following:

```setup
conda activate fortattack
pip install -r requirements.txt
```

Install clingo ASP solver as well.

## Running the Code
Use the following command to run the simulation environment with ad-hoc agent, two other guards, and three attackers, and to generate belief trees and answers to randomly generated queries.

```setup
python fortattack.py --test
```

To run axiom learning, run the axioms_learn.py file which calls the ad hoc agent implementation for learning.

