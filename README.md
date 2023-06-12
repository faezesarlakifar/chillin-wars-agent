# ChillinWars-Agent
## An Agent for Tron game
Our agent for the Tron game utilizes a combination of genetic algorithm and minimax for decision making. Here are the key statements of our approach:

- We have a minimax tree with fixed max depth size as a hyper parameter.
- We have also genetic popuation. our individuals represents paths in the minimax tree. 
- Define fitness for each path and then, select some individuals as parents and make next generation by them with mutatio probabilty of 0.1. (as a hyper parameter)
- Finally, we find the best path as a best individual. and the best action we will choose for next state, is the first node of best individual. (it means we analyze the fitness of the next n steps n and choose the path which give us better fitness. And then, choosing the first action of that path as minimax algorithm says.)

<br>This approach represents a combined AI-based algorithm, leveraging the power of both genetic algorithms and minimax to enhance decision making in the Tron game.
### Here is the problem description in details: [link](https://drive.google.com/file/d/1efJlmPG9kO5om_rzvnbNLBChglS3dRQ0/view?usp=sharing)
