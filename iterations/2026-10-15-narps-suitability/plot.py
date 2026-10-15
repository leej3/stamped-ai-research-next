"""Plot recorded pilot wall time; run with the root Pixi environment."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
runs = json.loads((HERE / "comparison.json").read_text())["runs"]
agent = np.array([r["agent_wall_seconds"] for r in runs]) / 60
setup = np.array([r["setup_and_launcher_overhead_seconds"] for r in runs]) / 60
plt.rcParams.update({"font.size": 12, "svg.fonttype": "none"})
fig, ax = plt.subplots(figsize=(8, 3.8), layout="constrained")
y = np.arange(len(runs))
ax.barh(y, setup, color="#bdcbd1", label="Preparation and launcher overhead")
ax.barh(y, agent, left=setup, color="#286a83", label="Native agent work")
for i, (a, s) in enumerate(zip(agent, setup)):
    ax.text(s + a / 2, i, f"{a:.2f} min", color="white", ha="center", va="center")
ax.set(yticks=y, yticklabels=["Pilot " + r["run"][-2:] for r in runs],
       xlabel="Elapsed minutes per run", xlim=(0, 7.5),
       title="Three baseline pilots completed in about five minutes of agent work")
ax.invert_yaxis()
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="upper left", bbox_to_anchor=(0, -0.24), frameon=False, fontsize=10)
output = HERE / "timing.svg"
fig.savefig(output, metadata={"Date": None})
output.write_text("\n".join(line.rstrip() for line in output.read_text().splitlines()) + "\n")
