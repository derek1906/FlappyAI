# FlappyAI
Q-Learning with a Flappy Bird simulator.

![FlappyAI Demo](/demo.gif)

## Why?
FlappyAI is an AI that uses simple Q-Learning trained on a custom Flappy Bird simulator. It is mainly created for learning purposes. If you are looking for Q-Learning libraries that are more efficient and does not mind the steep learning curve, try [TensorFlow](https://www.tensorflow.org/) instead.

## Structure
FlappyAI contains these main parts:

- `FlappyGame` - FlappyBird simulator
- `Trainer` - Q-Learning agent
- `ModelInterface` - Interface for the model used by the agent
- `main.py` - Part where everything connects together

## Dependencies
FlappyAI is written in Python. The required libraries include:

- `pygame` - Required for the graphics
- Standard Python2 libraries

## Extending FlappyAI to Other Games
Simply create a new interface and inherits from `ModelInterface` for your simulator.

```python
from qlearning import Trainer, ModelInterface

class MyInterface(ModelInterface):
    # interacts with your simulator

agent = Trainer(MyInterface())  # creates a new agent with your interface
agent.train()                   # starts the training
```

## How to Run
Type

    python main.py -h

for help. FlappyAI has three modes:

- interactive - No AI involved; Only human input
- train - Start the training process.
- test - Let AI plays the game

FlappyAI automatically looks for `qtable.p` in the current directory. It will create a new one if it cannot find one. This file is used to store the trained Q-table (KNAWLEDGE!). The Q-table file included in the repository is already trained, but if you want to retrain the agent, simply remove or rename the file.

During the training mode, press Ctrl+C to stop and store the Q-table to the file.

## Technical Details
### State Space
Assuming the game size is 640x480. Parameters considered by the AI are the following:

- Horizontal distance between bird and nearest pipe divided by 10 (i.e. 0 to 300/10 and 300+)
- Vertical distance between bird and nearest pipe (-480/10 to 480/10)
- Bird velocity (-10/5 to 20/5)

Resulting in a total of 43456 states.

The 2D space is discretized into 10x10 tiles, therefore the framerate of the AI must be reduced by a factor of 10 (i.e. game is running in 60fps and the agent will be running in 6fps.)

### Q-Learning Background
Q-Learning is a simple reinforcement learning algorithm that has three parameters:

- α - Learning rate
- γ - Discount factor
- ε - Exploration probability (only in ε-greddy Q-Learning)

Definitions:

- Let S be the set of all states and A be the set of all actions.
- We also define Q: S x A -> R, where R is the set of all real numbers.
- Then the algorithm is as follow:
    - Q(s\_t, a\_t) <- Q(s\_t, a\_t) + α (r\_t + γ maxOverAllActions(Q(s\_(t+1), a)) - Q(s\_t, a\_t))
    - Continues until it converges (or converges within epsilon.)
