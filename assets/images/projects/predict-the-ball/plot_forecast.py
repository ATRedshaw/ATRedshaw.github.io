"""Regenerate the portfolio chart with Python, matplotlib and NumPy."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, PowerNorm

matplotlib.use("Agg")
import matplotlib.pyplot as plt


directory = Path(__file__).resolve().parent
data = json.loads((directory / "forecast-snapshots.json").read_text(encoding="utf-8"))
snapshot = data["snapshots"][-1]
rows = snapshot["projections"]
probabilities = np.array([
    [row["finish_probabilities"][str(position)] for position in range(1, 21)]
    for row in rows
])
date = (
    datetime.fromisoformat(snapshot["updated_at"])
    .replace(tzinfo=ZoneInfo(data["timestamp_timezone"]))
    .astimezone(ZoneInfo("Europe/London"))
)

background = "#161A1D"
foreground = "#F4F1EA"
muted = "#A7B9B1"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12})
fig, ax = plt.subplots(figsize=(14, 10), facecolor=background)
ax.set_facecolor(background)
colours = LinearSegmentedColormap.from_list(
    "finish_probability", [background, "#354F49", "#719F8E", "#DCE8D6"]
)
# A curved colour scale keeps the spread of smaller probabilities visible.
heatmap = ax.imshow(
    probabilities,
    cmap=colours,
    norm=PowerNorm(gamma=0.55, vmin=0, vmax=60),
    aspect="auto",
)
ax.set_xticks(range(20), labels=range(1, 21))
ax.set_yticks(range(20), labels=[
    f"{row['team']}  ({row['mean_position']:.2f})" for row in rows
])
ax.tick_params(axis="both", colors=foreground, length=0, pad=8)
ax.set_xlabel("Final league position", color=foreground, labelpad=14)
ax.set_title("Where could each club finish?", color=foreground, fontsize=22, loc="left", pad=55)
ax.text(
    0, 1.045,
    f"{snapshot['season']}  |  {date.day} {date:%B %Y}, {date:%H:%M %Z}  |  "
    f"{snapshot['simulation_count']:,} simulations, {snapshot['fixtures_simulated']} fixtures remaining",
    transform=ax.transAxes, color=muted, fontsize=11,
)
for boundary in [0.5, 3.5, 16.5]:
    ax.axvline(boundary, color=foreground, alpha=0.25, linewidth=1)
for i, j in np.ndindex(probabilities.shape):
    probability = probabilities[i, j]
    if probability >= 5:
        ax.text(
            j, i, f"{probability:.0f}", ha="center", va="center", fontsize=9,
            color=background if probability >= 20 else foreground,
        )
for spine in ax.spines.values():
    spine.set_visible(False)
colourbar = fig.colorbar(heatmap, ax=ax, fraction=0.025, pad=0.025)
colourbar.set_ticks([0, 5, 10, 20, 40, 60])
colourbar.ax.tick_params(colors=foreground, length=0)
colourbar.set_label("Chance of finishing here (%)", color=foreground, labelpad=12)
colourbar.outline.set_visible(False)
fig.text(
    0.02, 0.025,
    "Saved PredictTheBall forecast. Clubs ordered by mean finish, shown in brackets. "
    "Cell labels show rounded percentages of at least 5%.",
    color=muted, fontsize=10,
)
fig.subplots_adjust(left=0.25, right=0.93, top=0.86, bottom=0.10)
fig.savefig(directory / "finish-probabilities.png", dpi=160, facecolor=background)
plt.close(fig)
