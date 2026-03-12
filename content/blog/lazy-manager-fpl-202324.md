Every August, millions of us convince ourselves that *this* is our year in Fantasy Premier League. We build elaborate spreadsheets, agonise over £4.0m backup defenders, and set alarms for the Friday night deadline. Then Gameweek 3 rolls around, Pep Guardiola benches our star captain, someone tears a hamstring, and we are left questioning all of our life choices.

I wanted to know if there was a lazier way to win. What if you built a squad before the first whistle of Gameweek 1 and literally never looked at it again? No frantic transfers. No captaincy stress. Just pure, unadulterated neglect.

Obviously a "set-and-forget" strategy is a terrible idea in the real world. You cannot predict injuries or wild swings in form. But as a thought experiment, it is absolute gold. I wanted to see exactly how many points a perfectly optimised, completely ignored FPL team could score if we had perfect hindsight for the 23/24 season. [The full GitHub repo for this project lives here](https://github.com/ATRedshaw/fpl-hindsight-optimiser).

## Building the Robot Manager

To figure this out, I wrote a Python script using the PuLP library. PuLP is fantastic for solving linear programming problems, which is just a fancy way of saying it finds the best possible outcome while juggling a bunch of strict rules.

The setup is split into two main parts. The optimisation engine ([basic_set_and_forget_optimisation.py](https://github.com/ATRedshaw/fpl-hindsight-optimiser/blob/main/set_and_forget/basic_set_and_forget_optimisation.py)) handles the heavy mathematical lifting. Meanwhile, the orchestrator notebook ([exploration_set_and_forget.ipynb](https://github.com/ATRedshaw/fpl-hindsight-optimiser/blob/main/set_and_forget/exploration_set_and_forget.ipynb)) pulls the raw player data from the official FPL API and feeds it into the engine.

I had to translate all the annoying FPL constraints into a mathematical format so the script would not try to field eleven strikers. The budget was capped at £100 million. The squad needed exactly 15 players with the correct positional limits. I also had to cap the number of players from a single club at three. 

The actual goal for the algorithm was simple. Maximise the total season points while factoring in the captain, the vice-captain and the bench players.

Here is the core logic that drives the search.

```python
def basic_set_and_forget(player_gameweek_df, bench_multiplier, budget=1000):
    """
    Solves the basic 'set and forget problem' using PuLP. The set and forget problem considers a team
    that is chosen from gameweek 1, with a budget of 100m, and no further changes are made.
    This basic modelling does not explicitly consider substitutions when players do not feature, 
    or vice captain swapping when the captain does not feature. For this reason, it will not be fully optimal, 
    but the use of the bench multiplier, and later comparisons of different values for this, should enable
    optimisation to a relatively high level.

    Args:
        player_gameweek_df (pd.DataFrame): The player gameweek data.
        bench_multiplier (float): The multiplier for bench players (also applied to the vice captain).
        budget (float): The budget for the team (million value divided by 0.1m).

    Returns:
        Tuple[List[LpVariable], List[LpVariable], List[LpVariable], List[LpVariable]]: The decision variables for lineup, bench, captaincy, and vice_captaincy.
    """
    df = player_gameweek_df[["id", "total_points", "short_name", "positions", "start_cost"]]   
    
    player_ids = df['id'].tolist()
    player_count = len(player_ids)

    # Set up the problem
    model = plp.LpProblem("basic-set-forget", plp.LpMaximize)

    # Define the decision variables
    lineup =[
        plp.LpVariable(f"lineup_{i}", lowBound=0, upBound=1, cat="Integer")
        for i in player_ids
    ]
    captaincy =[
        plp.LpVariable(f"captaincy_{i}", lowBound=0, upBound=1, cat="Integer")
        for i in player_ids
    ]
    vice_captaincy =[
        plp.LpVariable(f"vice_captaincy_{i}", lowBound=0, upBound=1, cat="Integer")
        for i in player_ids
    ]
    bench =[
        plp.LpVariable(f"bench_{i}", lowBound=0, upBound=1, cat="Integer")
        for i in player_ids
    ]

    # Set the objective function maximise points
    model += sum((lineup[i] + captaincy[i] + (bench_multiplier * vice_captaincy[i]) + (bench_multiplier * bench[i])) * df["total_points"][i] for i in range(player_count))

    # Set the budget constraints
    model += sum((lineup[i] + bench[i]) * df["start_cost"][i] for i in range(player_count)) <= budget

     # GK constraints
    model += sum(lineup[i] for i in range(player_count) if df['positions'][i] == 'GK') == 1
    model += sum(lineup[i] + bench[i] for i in range(player_count) if df['positions'][i] == 'GK') == 2

    # DEF constraints
    model += sum(lineup[i] for i in range(player_count) if df['positions'][i] == 'DEF') >= 3
    model += sum(lineup[i] + bench[i] for i in range(player_count) if df['positions'][i] == 'DEF') == 5

    # MID constraints
    model += sum(lineup[i] for i in range(player_count) if df['positions'][i] == 'MID') >= 2
    model += sum(lineup[i] + bench[i] for i in range(player_count) if df['positions'][i] == 'MID') == 5

    # FWD constraints
    model += sum(lineup[i] for i in range(player_count) if df['positions'][i] == 'FWD') >= 1
    model += sum(lineup[i] + bench[i] for i in range(player_count) if df['positions'][i] == 'FWD') == 3

    # Team constraints
    model += sum(lineup) == 11
    model += sum(bench) == 4
    model += sum(lineup) + sum(bench) == 15
    model += sum(captaincy) == 1
    model += sum(vice_captaincy) == 1
    for teams in df['short_name'].unique():
        model += sum(lineup[i] + bench[i] for i in range(player_count) if df['short_name'][i] == teams) <= 3
    
    for i in range(player_count):
        model += (lineup[i] + bench[i]) <= 1
        model += (lineup[i] - captaincy[i]) >= 0
        model += (lineup[i] - vice_captaincy[i]) >=0
        model += (captaincy[i] + vice_captaincy[i]) <= 1

    plp.LpSolverDefault.msg = 0
    model.solve()

    return lineup, bench, captaincy, vice_captaincy
```

## Handling the FPL Nonsense

FPL is never quite that straightforward. To make this accurate, the script had to handle the weird edge cases that usually ruin our weekends.

Take auto-substitutions. If a starting player gets zero minutes, the bench players step up based on their order and the valid formation rules. The model actually optimises the bench order to squeeze every drop of value from those unexpected cameos. 

Then there is the vice-captain problem. A vice-captain only gets double points if your main captain completely misses the game. The script accounts for this, picking a vice-captain who is perfectly positioned to haul exactly when the main captain gets rested. It took running a few different refined combinations to get this working smoothly without burning up my CPU.

## The Results

Let's get straight to the numbers. My meticulously calculated, completely ignored dream team scored 2,656 points.

That score would have secured a top 250 finish globally. Out of more than 11 million managers, a team that literally did not make a single transfer all year beat 99.99% of them. 

I should probably point out that this is entirely fueled by the unfair advantage of hindsight. The code knew exactly who would score every single week. But it is still hilarious to see how high the ceiling is for pure inaction.

### Man vs Machine

For context, my actual human-managed FPL season was a disaster. I finished in 171,811th place. My glorious 1,326th place finish and Liverpool Cup victory from the year prior feels like ancient history.

Figure 1 shows the depressing gap between my sweaty, stressed-out tinkering and the robot's serene climb up the ranks.

![image](assets/images/blogs/lazy-manager-fpl-202324/cummulative_points_own_vs_optimised.png)
*Figure 1 The cumulative points scored by me vs the optimal set-and-forget team.*

The optimal team did not just win big. It was relentlessly consistent. Figure 2 shows how it compared to the global average week by week.

![image](assets/images/blogs/lazy-manager-fpl-202324/optimised_difference_to_average_by_gw.png)
*Figure 2 The difference in points scored by the optimised set-and-forget team vs the global average.*

Over 38 gameweeks, the static squad only dipped below the global average five times. For most of the year it was banking solid green arrows, completely unfazed by blank and double gameweeks.

Figure 3 plots out the distribution of those points. 

![image](assets/images/blogs/lazy-manager-fpl-202324/optimised_points_distribution_hist.png)
*Figure 3 The distribution of points scored by the optimal set-and-forget team.*

The bell curve peaks right around 70 to 80 points per gameweek. That translates to almost every single player in the squad returning an average of 6 points a week. It is the kind of steady drip-feed of points that destroys mini-leagues by April.

### The Dream Team Breakdown

The really fun part is looking at exactly who made the cut. Figure 4 is my favorite chart from the whole project. It breaks down the points by player, including the hidden value of bench points and vice-captaincy.

![image](assets/images/blogs/lazy-manager-fpl-202324/set_and_forget_player_point_breakdown.png)
*Figure 4 The breakdown of players' contribution to the total points tally.*

Look at Double Gameweek 34. Vice-Captain Phil Foden went massive, but bench players like Jean-Philippe Mateta and Jarrad Branthwaite also auto-subbed in for massive hauls. It was the absolute perfect storm of timing and opportunity.

Figure 5 groups the total points by position.

![image](assets/images/blogs/lazy-manager-fpl-202324/set_and_forget_total_points_by_position.png)
*Figure 5 The breakdown of total points scored by each position.*

Midfielders absolutely dominated, which makes sense given the clean sheet bonuses and how many goals they score. But the defenders actually outscored the forwards overall, mostly thanks to Arsenal forgetting how to concede goals last season. It proves that a rock-solid defense is still completely mandatory.

Finally, Figure 6 shows the total points contributed by each specific player.

![image](assets/images/blogs/lazy-manager-fpl-202324/set_and_forget_total_team_points_contribution.png)
*Figure 6 The total points scored by each player in the optimal setup.*

Jean-Philippe Mateta is the absolute hero here. He spent half the season rotting on the bench, but his crazy late-season form meant his auto-sub cameos rivaled the starting Arsenal defenders for total output. It is a great reminder that explosive attacking form will always bail you out in FPL.

## What Comes Next

Basking in the glory of an imaginary hindsight team is fun, but it is effectively cheating. You cannot run an FPL team on past data. You have to guess what Pep is going to do next Saturday.

This project was just a stepping stone. My next goal is to turn this hindsight engine into a forward-looking predictive tool. If I can feed historical data and statistical models into the optimiser, maybe it can actually map out the smartest transfers before the deadline. 

I also want to look at rolling optimisation. Instead of picking one team for 38 weeks, what if the algorithm is allowed to make one transfer a week? That would find the true absolute maximum points tally physically possible under the rules of the game.

Until I get that working, I will probably keep making terrible transfer decisions on Friday nights. But at least now I know that sometimes doing absolutely nothing is statistically the best move you can make.
