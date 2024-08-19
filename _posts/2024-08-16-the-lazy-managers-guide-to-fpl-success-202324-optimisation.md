---
title: "The Lazy Manager's Guide to FPL Success: 2023/24 Set-and-Forget Optimisation"
date: 2024-08-16 19:30:00 BST
categories: [Fantasy Games,  Fantasy Premier League]
tags: [fpl, fantasy premier league, football, optimisation, data, statistics, modelling, python, mathematics]
math: true
---

The start of a new Premier League season always brings a familiar wave of excitement. For Fantasy Premier League managers, this means meticulous planning, endless tinkering, and the intoxicating dream of outsmarting millions of rivals. But what if there was another way? A path to FPL glory paved not with relentless optimisation, but with deliberate inaction?  

## Understanding the Set-and-Forget Strategy

That's where the intriguing concept of the "set-and-forget" team comes into play. Imagine this: you build your squad before the first whistle blows on Gameweek 1, and then...you walk away. No transfers, no agonizing over captaincy choices, no last-minute scrambles to field a full XI. It's the most relaxing fantasy strategy: achieving success through masterful inactivity.

Of course, the set-and-forget strategy is more of a thought experiment than a practical approach. Season-long FPL success hinges on adapting to the ever-changing landscape of player form, injuries, and fixtures. Yet, I found myself captivated by the "what if" scenario. What if, through a stroke of genius (or perhaps a healthy dose of luck), you could assemble a team capable of thriving in complete stasis? Just how effective could a perfectly optimised, completely ignored FPL team be?

This curiosity, coupled with my desire to explore the power of optimisation techniques using libraries like PuLP, set the stage for this project. I wanted to delve into the world of set-and-forget FPL optimisation, not as a blueprint for real-world management, but as a fascinating exercise in maximizing potential within seemingly absurd constraints. So this is exactly what I explored for the 23/24 season just gone - [the full GitHub repo for this, and future hindsight optimisations in the FPL sphere, can be found here.](https://github.com/ATRedshaw/fpl-hindsight-optimiser)

## Optimisation Methodology

To bring this set-and-forget experiment to life, I harnessed the power of Python. My weapon of choice? The PuLP library, a versatile tool for tackling optimisation problems.

The project's core comprises two key components:

1. **The Optimisation Engine:**  ([basic_set_and_forget_optimisation.py](https://github.com/ATRedshaw/fpl-hindsight-optimiser/blob/main/set_and_forget/basic_set_and_forget_optimisation.py)) -  This is where the magic happens. This script houses the optimisation model itself, a symphony of mathematical equations, constraints and simulations designed to pinpoint the theoretical best set-and-forget team.

2. **The Orchestrator:** ([exploration_set_and_forget.ipynb](https://github.com/ATRedshaw/fpl-hindsight-optimiser/blob/main/set_and_forget/exploration_set_and_forget.ipynb)) - This notebook acts as the conductor, handling data retrieval, feeding it into the optimisation model, and then presenting the results in a visually insightful manner.

Here's how the optimisation process unfolded:

1. **Data Acquisition:**  The foundation of any data-driven endeavor is, well, data! Using the official FPL API, I pulled in a treasure trove of player statistics, encompassing everything from points scored in each gameweek to player costs.

2. **Model Building:** With data in hand, it was time to build the optimisation model using PuLP. 

3. **Constraint Definition:** FPL is a game of rules, and our optimisation model needed to respect them. This involved translating the rules of FPL (budget limits, formation constraints, etc.) into mathematical expressions that PuLP could understand - ensuring the model wouldn't assemble an illegal squad.

4. **Objective Setting:**  Every optimisation problem needs a goal.  In our case, it was maximizing total points across the entire FPL season. This involved accounting for not just starting players, but also the often-overlooked contributions of captain and vice-captain choices and of bench players from those glorious auto-substitutions.

5. **The Grand Solution:**  With the stage set and the objective clear, it was time to unleash PuLP and get a solution to the problem.

The Python function you see below represents the heart of this optimisation engine. Don't worry, we won't get bogged down in the code itself.  But for those curious, this function encapsulates the core logic that drives the search for the optimal set-and-forget team.

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
    lineup = [
        plp.LpVariable(f"lineup_{i}", lowBound=0, upBound=1, cat="Integer")
        for i in player_ids
    ]
    captaincy = [
        plp.LpVariable(f"captaincy_{i}", lowBound=0, upBound=1, cat="Integer")
        for i in player_ids
    ]
    vice_captaincy = [
        plp.LpVariable(f"vice_captaincy_{i}", lowBound=0, upBound=1, cat="Integer")
        for i in player_ids
    ]
    bench = [
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

This function implements the core logic of our set-and-forget optimisation, but there is a considerable amount of additonal optimisation code contained in the repository linked. Here's a breakdown of the key rules and constraints implemented in the model:

| Rule | Description |
|------|-------------|
| Budget | Total team cost must not exceed £100 million (represented as 1000 in the model) |
| Squad Size | 15 players (11 starting + 4 bench) |
| Position Requirements | 2 GK, 5 DEF, 5 MID, 3 FWD |
| Formation | At least 1 GK, 3 DEF, 2 MID, 1 FWD in the starting lineup |
| Team Limit | Maximum 3 players from any single Premier League team |
| Captaincy | 1 captain and 1 vice-captain must be selected |
| Player Uniqueness | A player can't be in both the starting lineup and on the bench, be C and VC, etc.|

While these core rules formed the bedrock of our optimiser, FPL has a knack for throwing curveballs. To truly capture the essence of a season-long campaign, we needed to account for even more nuanced scenarios, leading to additional refinements in the code:

**The Art of the Auto-Sub**: When a starting player fails to grace the field, your bench players leap into action (or at least they do in the digital realm of FPL). The order in which they're chosen, however, depends on both their position and your existing formation. Our model carefully considers these substitution rules, optimising bench order to maximize potential points from those unexpected cameos.

**The Vice-Captain Conundrum**: We often think of the vice-captain as simply the player with the second-highest score. But in reality, their points are only doubled if the captain doesn't play. Our code factors in this subtle but crucial distinction, ensuring the selected vice-captain is truly the one best positioned to inherit the armband and deliver those sweet, sweet double points.

Handling this was pursued in a slightly different, and in hindsight not the most efficient way, where multiple optimisations were run using various refined combinations of bench players, orders, captaincy choices, etc.. This was the easiest way to implement it once the process had got underway, and still maintained a relatively low computational cost.

## Results and Insights

### Points Scored & Overall Rank
The moment of truth had arrived. After fine-tuning constraints, wrestling with substitutions, and letting the optimisation engine run its course, we had our answer. The fully optimised, meticulously crafted, and utterly ignored set-and-forget team achieved a staggering 2656 points.

To put that into perspective, this dream team would have secured a top 250 finish in the world, outperforming the vast majority of the 11 million+ FPL managers globally. Let that sink in for a moment: a team selected once, untouched throughout the season, could theoretically achieve a level of success most active managers only dream of.
Now, before we all resign ourselves to a future of FPL passivity, let's inject a dose of reality. This remarkable achievement was fueled by the unfair advantage of hindsight. Our optimiser had access to the entire season's data, a luxury no manager enjoys in the real world.

### Comparison to my Own Team

Speaking of reality, let's just say my own FPL season played out in stark contrast to this optimised ideal. A disappointing 171,811th place finish served as a humbling reminder that real-world FPL involves a potent cocktail of skill, luck, and the occasional emotional breakdown. (My 1,326th place finish and triumphant Liverpool Cup victory the previous year feels like a distant memory).

Figure 1 below vividly illustrates the chasm between my season-long struggle and the optimised team's serene ascent:

![image](/assets/img/lazy-managers-guide-to-fpl-success-202324/cummulative_points_own_vs_optimised.png)
_Figure 1: The cumulative points scored by me vs. the optimal set-and-forget team._

### Comparison to the Average Team

The optimised team's success wasn't just about a high overall score, it was about the *way* it achieved those points. This was a masterclass in consistency, steadily outperforming the average FPL manager week after week. 

Figure 2 showcases this impressive consistency with remarkable clarity:

![image](/assets/img/lazy-managers-guide-to-fpl-success-202324/optimised_difference_to_average_by_gw.png)
_Figure 2: The difference in points scored by the optimised set-and-forget team vs. the average per gameweek._

Throughout the entire 38-gameweek season, our static squad lost out to the average team only five times. And on all but one of those occasions (Gameweek 1's teething problems), the margin was razor-thin. On the flip side, the optimised team racked up a remarkable number of victories over the average player, particularly as the season wore on and those lucrative double gameweeks rolled around.

This trend of steady gains is further emphasized in the points distribution shown in Figure 3:

![image](/assets/img/lazy-managers-guide-to-fpl-success-202324/optimised_points_distribution_hist.png)
_Figure 3: The distribution of points scored by the optimal set-and-forget team._

The bell curve centers around a sweet spot of 70-80 points per gameweek.  Breaking it down, that translates to an average of 5.8 to 6.6 points per player per gameweek (remember, the captain counts as an extra player in this calculation). Imagine that: a near-guaranteed return from almost every single member of your team, every single week. This level of consistency is the stuff of FPL legend, and it's no surprise that a team capable of achieving it would leave countless managers trailing in its wake.

### Individual Player Contributions to the Optimal Set-and-Forget Team

While the optimised team's overall points tally is impressive, it's the individual player contributions that weave a compelling narrative about the dynamics of set-and-forget success. Figure 4, my personal favorite visualization from this project, beautifully captures this interplay:

![image](/assets/img/lazy-managers-guide-to-fpl-success-202324/set_and_forget_player_point_breakdown.png)
_Figure 4: The breakdown of players' contribution to the total points tally in the optimal set-and-forget team._

This visual masterpiece not only reveals each player's point contribution but also illuminates the often-hidden impact of bench players and vice-captaincy. Take Double Gameweek 34, for example: Vice-Captain Foden shines alongside unexpected heroes Mateta and Branthwaite (both bench players), highlighting how the perfect storm of timing and opportunity can elevate even the most unassuming FPL assets.

Examining the total points by position in Figure 5 reveals further insights:

![image](/assets/img/lazy-managers-guide-to-fpl-success-202324/set_and_forget_total_points_by_position.png)
_Figure 5: The breakdown of total points scored by each player's position in the optimal set-and-forget team._

It's hardly surprising that midfielders reign supreme, given their goal-scoring potential, goalscoring and clean sheet bonuses, on top of the fact that both the captain and vice-captain slots fall within this category. However, the defenders, bolstered by the defensive dominance of Arsenal in the 23/24 season, put in a stellar performance, narrowly surpassing the forwards in total points. This underscores the value of investing in a solid backline, even in a set-and-forget approach.

Finally, Figure 6 provides a detailed look at each player's total points tally, revealing a compelling 'cult-hero' story:

![image](/assets/img/lazy-managers-guide-to-fpl-success-202324/set_and_forget_total_team_points_contribution.png)
_Figure 6: The total points scored by each player in the optimal set-and-forget team._

Enter Jean-Philippe Mateta, our unlikely hero. Despite starting on the bench, Mateta's late-season surge in form propelled him to a points tally that rivaled even the mighty Arsenal defenders. Keep in mind, this is a player who was auto-subbed into the team for only half of the season!  

Mateta's performance serves as an ultimately powerful reminder: while a consistent defensive foundation is crucial for accumulating clean sheet points, nothing can truly replace the explosive impact of a player in red-hot, goal-scoring form.  

##  The Limits of Hindsight and the Quest for Forward-Looking Optimisation

As much fun as it's been to bask in the glory of our optimised, hindsight-powered FPL team, it's essential to acknowledge the limitations inherent in this approach. Our journey into the world of set-and-forget optimisation has revealed some insightful, and slightly disheartening, truths:

1. **The Hindsight Bias Conundrum:**  Our model benefitted from an unfair (and unrealistic) advantage: knowing exactly how every player would perform throughout the entire season. In the real world, FPL managers grapple with uncertainty, making educated guesses about player form, injuries, and the whims of Pep Guardiola.  Attempting to perfectly predict the optimal set-and-forget team at the start of the season is akin to finding a needle in an infinitely large haystack of player combinations, captaincy choices and bench orders. 

2. **The Static Strategy Paradox:**  Let's face it: the true joy of FPL lies in its dynamic nature. We love it when we're flying and hate it when we're down. We crave the weekly transfer tussles, the strategic deployment of chips, and the smug satisfaction of a perfectly timed differential captaincy pick. A set-and-forget approach, while surprisingly effective in this idealized scenario, ultimately strips away the very essence of what makes FPL so captivating. 

However, this exploration isn't meant to be the final word. Instead, it lays the groundwork for even more intriguing optimisation challenges to come:

* **Embracing the Power of Prediction:**  My sights are firmly set on evolving this model from a hindsight-driven curiosity into a powerful predictive tool.  By incorporating historical data, pre-season analysis, and sophisticated statistical models, we can attempt to forecast player performance and optimise teams *before* a single ball is kicked. Imagine a tool that helps you map out your transfers and strategically deploy your chips for maximum impact. 

* **Unleashing the Rolling Optimisation Machine:** Another avenue ripe for exploration is the concept of "rolling optimisation."  Instead of a single, season-long optimisation, we could create a model that dynamically adjusts the team on a weekly basis, making transfer decisions based on the latest data and maximizing points within the constraints of FPL's budget and transfer rules. This wouldn't just be about finding a single "optimal" team, but about mapping out the theoretical upper limits of FPL success, revealing just how many points are truly attainable with perfect foresight and ruthless optimisation. 

## Conclusion
The "Lazy Manager's Guide to FPL Success" might seem like an oxymoron. After all, the heart of FPL lies in the weekly tinkering, the transfer dilemmas, and the strategic deployment of chips. However, this exploration into set-and-forget optimisation reveals a surprising truth: even with zero in-season management, a shockingly competitive FPL score is attainable.

While this experiment shouldn't be misconstrued as an endorsement for complete FPL apathy, it underscores the inherent volatility of the game and the significant role luck plays in determining the ultimate outcome. The optimised team's performance, while remarkable, is a product of hindsight. Replicating such success in a real-world scenario, where predicting the future is impossible, is simply not realistic.

Nevertheless, this project provides valuable insights for pragmatic FPL managers. By understanding the potential of a well-structured, albeit static, team, managers can gain a deeper appreciation for the importance of thoughtful pre-season planning. It also highlights the potential pitfalls of overthinking and over-managing your team throughout the season. Sometimes, a little bit of calculated laziness, combined with a dash of pre-season foresight, can go a long way in the unpredictable world of FPL.