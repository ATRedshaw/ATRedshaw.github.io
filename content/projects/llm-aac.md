## What Is AAC?

Augmentative and Alternative Communication, or AAC, refers to any system that supplements or replaces speech for people who cannot communicate verbally. This might be someone with cerebral palsy, ALS, autism or any number of conditions that affect speech production. Traditional AAC devices present vocabulary in categorised, folder-based grids: the user navigates between folders, selects one word at a time and gradually assembles a sentence. It works, but it is slow, cognitively demanding and roughly analogous to trying to write an email using only a printed phonebook.

This project asks a straightforward question: can a context-aware, vision-augmented suggestion feed powered by a multimodal large language model meaningfully improve communication speed and reduce physical effort compared to the conventional static folder approach?

## The Experiment

I built a browser-based AAC research tool from scratch in HTML, CSS and JavaScript. The interface presents participants with a scene photograph alongside a target sentence they must construct using the available vocabulary. Scenarios were drawn from a pool of real-world environments ranging from a pharmacy counter and a bus stop to a gym and a jewellery store.

Each participant completes ten scenarios, alternating between two interface conditions:

- **Static mode**: A conventional folder-based vocabulary grid. Words are organised into thematic categories (pronouns, actions, food, health and so on) and participants navigate between folders to build their sentence.
- **Vision mode**: The same grid is available, but a dedicated "Context" tab is added. On scenario start, the scene photograph is passed to a multimodal LLM (Meta Llama 4 Maverick via the Groq API) which returns a contextually relevant word list. These appear as a single flat tile grid, eliminating the need to hunt through folders.

</br>

Before any timed trials begin, participants complete a sandbox session to explore the interface without data being recorded, reducing first-encounter friction. Every interaction is then logged at the event level: timestamped keystrokes, tab switches, AI suggestion selections and real-time similarity scores. Sentence similarity is computed using a token-level matching algorithm with trigram-based Jaccard similarity for fuzzy matching, so "hurt" sensibly matches "hurts".

## What Is Being Measured

Three core metrics are extracted per completed task:

**Communication Rate (WPM)** is words entered divided by task duration, calculated both raw and with the AI's processing latency subtracted. The latter represents a theoretical ceiling assuming instantaneous inference, which is not quite where we are yet but the direction of travel is encouraging.

**Physical Interaction Cost** is the total number of UI interactions required to complete a sentence. Folder selections and AI taps count as one click per word. Keyboard input is charged at one click per character plus one for the enter key, because typing "withdraw" on a virtual keyboard is not the same as tapping a single pre-generated tile and conflating the two would paint a flattering but dishonest picture.

**Selection Ratio** is physical interactions divided by word count. A ratio of 1.0 means every word required exactly one tap. The higher this number climbs, the more folder navigation and typing effort was involved.

## Early Results

Data collected so far points consistently in the same direction across all three metrics. The analysis is performed in Python using pandas, scipy and seaborn, and is updated as new sessions arrive.

### Communication Speed

Vision mode participants are completing tasks at a meaningfully higher words-per-minute rate than those using Static mode, a difference that has reached statistical significance. When task duration is adjusted to remove AI processing latency the advantage grows further, suggesting that a faster inference backend would translate directly into additional speed gains rather than simply inflating the headline number.

### Physical Effort

The reduction in interaction cost is where Vision mode's advantage is most apparent. Participants require substantially fewer total interactions to complete a Vision scenario compared to Static, and the selection ratio tells the same story more sharply: considerably fewer clicks per word. For a user group in which motor fatigue is a genuine clinical consideration, a near-halving of required interactions is a practically meaningful result rather than a statistical curiosity.

### Task Duration

Raw task duration has not yet reached significance, which reflects the drag of AI inference latency on real-world performance. Once that latency is removed from the calculation the adjusted duration difference does reach significance, indicating that network delay rather than user behaviour is the primary bottleneck. Blame the internet, not the interface.

### Word Entry Strategy

In Vision mode, the majority of words are selected directly from AI suggestions, with keyboard entry dropping sharply compared to Static mode. This matters because a sceptic might reasonably worry that participants simply ignored the contextual suggestions and fell back on the familiar folders anyway. The data says otherwise: participants adopted the AI feed as their primary word source, and the LLM was generating vocabulary relevant enough to trust. A high folder-usage rate in Vision mode would have suggested the suggestions were poor. That is not what the data shows.

### Keystroke Saving Rate

The global Keystroke Saving Rate (KSR), a standard efficiency metric in AAC research, currently sits at a level suggesting Vision mode is eliminating roughly two in every five user interactions compared to the conventional folder-based approach. Whether that figure holds as the dataset grows is the interesting question.

## Status, Limitations and What Comes Next

This is an active, ongoing project. Data collection is continuing across a broader range of participants and devices, with the analysis pipeline updating incrementally as new sessions arrive. The current results are treated as early indicative findings rather than final conclusions, though the consistency across the metrics collected so far is encouraging.

There are known limitations that the full write-up will address directly. The current sample skews towards neurotypical participants who are comfortable with technology, which is about as far from the primary AAC user population as it is possible to get. Results from this group establish a useful performance ceiling but say little about the experience of someone with motor impairments, fatigue-driven attention limits or no prior exposure to grid-based communication. Recruitment is intentionally broadening to address this. There is also a counterbalancing consideration: scenario order is randomised per participant but the study has not yet reached the cohort size needed for a fully balanced within-subjects design, meaning learning effects across the ten trials cannot be entirely ruled out. The manual finish mechanism, which allows participants to submit a sentence that conveys the correct meaning without hitting the automatic similarity threshold, introduces a small amount of subjective judgement into the completion criteria, and those trials are flagged and reviewed separately in the analysis.

The write-up is developing alongside the data. Whether the early picture holds at scale is, of course, the whole point.