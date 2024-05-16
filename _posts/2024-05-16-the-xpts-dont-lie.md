---
title: "The xPts Don't Lie: Why the xG Naysayers Need to Open their Arms to Modern Model Metrics"
date: 2024-05-16 15:00:00 BST
categories: [Football Analytics]
tags: [xG (expected goals), machine learning, data, analytics, statistics, football]
math: true
---

Despite their ever-growing presence in the modern game, advanced analytics continue to be dismissed by many as nothing
more than a meaningless gimmick. Professionally however, there has been a continual, sustained adoption of these approaches across all facets of the game. Having recently written a dissertation in which I developed and applied an xG model, I have dug further into some of the numbers.

## What is xG (Expected Goals)?
Expected goals adopts a machine learning approach in order to quantitavely evaluate the quality of a shot. Models consider a range of potential influencing variables, including (but not limited to): shot coordinates, goalkeeper positioning, shot scenario, part of the body used and the preceeding action. The output values fall in the range of 0 and 1, where the greater the xG value, the more likely a shot is to result in a goal. This is a significant improvement on baseline metrics, such as shot count, which fail to sufficiently capture shot quality. I'll likely cover development of an xG model in a separate post, but for this use-case, lets assume we already have a model producing xG value outputs.

## Monte Carlo Simulation - xPts
Given the probabilistic nature of these model outputs, they can be used to simulate games using random number generation. Repeating this process many times over for all shots in a game can provide an indication on the average match result, allowing for the calculation of an xPts (expected points) value. Consider the example:

```
Team A shot xG values: [0.08, 0.32, 0.05]
Team B shot xG values: [0.46, 0.28]
```

Team A has 3 shots and Team B has 2 shots respectively. Now lets consider simulating this game for one single instance, using random number generation.

### Single Match Simulation
#### Code
```python
import random

# Initialise the shots
team_a_shots = [0.08, 0.32, 0.05]
team_b_shots = [0.46, 0.28]

# Simulate the home shots (Team A)
home_goals = 0
for shot in team_a_shots:
  random_num = random.random()
  print('Shot xG:', shot)
  print('Random Number:', random_num)

  # A shot is simulated as a goal if the random number is less than or equal to 
  # the shot xG value. This ensures the probability of the simulated value
  # aligns with the xG value.
  if shot >= random_num:
    home_goals += 1
    print('SIMULATED GOAL')
  else:
    print('SIMULATED NO GOAL')

# Simulate the away shots (Team B)
away_goals = 0
for shot in team_b_shots:
  random_num = random.random()
  print('Shot xG:', shot)
  print('Random Number:', random_num)

  if shot >= random_num:
    away_goals += 1
    print('SIMULATED GOAL')
  else:
    print('SIMULATED NO GOAL')


print(str(home_goals) + ' - ' + str(away_goals))
```
#### Results
A shot is simulated to be a goal if the random number generated for the shot is less than or equal to the shot xG. This ensures the probability of generating the goal remains consistent with the xG value. A random run for this code fragment produced the following:

$$
\begin{array}{|c|c|c|c|}
\hline
\text{Team} & \text{Shot xG} & \text{Random Number} & \text{Simulated Result} \\
\hline
\text{A} & 0.08 & 0.99 & \text{NO GOAL} \\
\hline
\text{A} & 0.32 & 0.02 & \text{GOAL} \\
\hline
\text{A} & 0.05 & 0.34 & \text{NO GOAL} \\
\hline
\text{A} & 0.15 & 0.54 & \text{NO GOAL} \\
\hline
\text{B} & 0.46 & 0.09 & \text{GOAL} \\
\hline
\text{B} & 0.28 & 0.68 & \text{NO GOAL} \\
\hline
\end{array}
$$

This gives an overall result of 1-1, and so in this instance, we would expect both teams to earn a single point. But what if we simulate this many times over, generating new random numbers each time. Repetition of this process should reduce the high levels of variance seen in a single simulation, therein allowing for the calculation of an expected points (xPts value). The above code can be minorly adapted in order to accomplish this:

### Repeated Match Simulation
#### Code
```python
import random

def simulate_game(team_a_shots, team_b_shots):
  """
  Simulates a single game.

  Args: 
    - team_a_shots (list): List of xG values for shots by Team A
    - team_b_shots (list): List of xG values for shots by Team B
  """
  # Simulate the home shots (Team A)
  home_goals = 0
  for shot in team_a_shots:
    random_num = random.random()

    # A shot is simulated as a goal if the random number is less than or equal to 
    # the shot xG value. This ensures the probability of the simulated value
    # aligns with the xG value.
    if shot >= random_num:
      home_goals += 1
    else:
      continue

  # Simulate the away shots (Team B)
  away_goals = 0
  for shot in team_b_shots:
    random_num = random.random()

    if shot >= random_num:
      away_goals += 1
    else:
      continue

  # Return the home and away goals for a single simulation.
  return home_goals, away_goals

if __name__ == '__main__':
  # Initialise the shots.
  team_a_shots = [0.08, 0.32, 0.05]
  team_b_shots = [0.46, 0.28] 

  # Setup a counter for each of the possible results.
  a_win = 0
  b_win = 0
  draw = 0

  # Carry out 100,000 simulations.
  for i in range(1,100001):
    a_goals, b_goals = simulate_game(team_a_shots, team_b_shots)

    # Update the counter for the relevant result.
    if a_goals > b_goals:
      a_win += 1
    elif b_goals > a_goals:
      b_win += 1
    else:
      draw += 1

# Print the results.
print('Team A Wins:', a_win)
print('Team B Wins:', b_win)
print('Draws:', draw)
```
#### Results
For 100,000 simulations, an example code run produces the following results:

$$
\begin{array}{|c|c|}
\hline
\text{Result} & \text{Count} \\
\hline
\text{Team A Wins} & 17809 \\
\hline
\text{Team B Wins} & 40972 \\
\hline
\text{Draw} & 41219 \\
\hline
\end{array}
$$

Given we know that a win is worth 3 points, a draw is worth 1 point and a loss is worth 0 points, we can take the average of these results to generate an xPts value for each team: 

$$
\text{Expected Points} = \frac{(\text{Team Wins} \times 3) + (\text{Team Draws} \times 1)}{n \text{ simulations}}
$$

As such, for our example with 100,000 simulations, the xPts are as follows:

$$
\text{Expected Points for Team A} = \frac{(17809 \times 3) + (41219 \times 1)}{100,000} = 0.95\\
$$

$$
\text{Expected Points for Team B} = \frac{(40972 \times 3) + (41219 \times 1)}{100,000} = 1.64\\
$$

Despite Team A taking more shots, the overall higher quality of shots taken by Team B is likely to yield more points in the average game featuring these shots. 

It's all well and good being able to generate these values, but given the resistance of many football fans to using xG in the first place, it is key to pinpoint the wider correlations. 

## The Overarching Correlations
In order to test this approach, real-game football data was simulated using a custom xG model on **3 seasons worth of data** (16-17, 18-19 and 21-22). This was **done for each of the 'big 5 European Leagues'**, i.e. the Premier League, Serie A, Ligue 1, La Liga and Bundesliga. This ultimately provided **seasonal data for $\approx{300}$ teams**. After simulating all of the shots in all of the matches for theses seasons, comparisons could then be drawn between a team's actual points and expected points. This could also be done in relation to their actual league finishing position vs their finishing position based on an expected points league table. The overall results were damning.

The average (absolute) deviation of a teams actual points value from their xPts value was a **mere 6.95 points across an entire season**, equal to **approximately 0.18 - 0.2 xPts per game** (depending on the size of the league). This translated to an approximate (absolute) deviation between actual and expected finishing position of **2.44 positions**.

Pearson's Correlation Coefficient confirms the strength of these positive correlations, with a correlation of 0.88 between points and xPts, and 0.83 between finishing position and expected finishing position. Given both p-values tend incredibly close to 0 (and given a threshold of 0.05), the null hypothesis that xPts do not correlate with actual team performance when considering a season-long scope can be confidently rejected. 

## Conclusions
The long run performance of this style of expected points simulation is **hugely correlative**, and **massively statistically significant**. Given this is founded purely on the outputs of xG models, it is clear the benefits that can be reaped from these data-based approaches is monumental. Widespread adoption allows for a more nuanced representation of the game, supporting decision-making processes and enabling more precise quantifiable metrics. For these reasons it is clear that these probabilistic styles of machine learning models are here to stay in football. Embracing them now will only be beneficial in improving long-term performance in relation to any footballing context, from player scouting to Fantasy Football.