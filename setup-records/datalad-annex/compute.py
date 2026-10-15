#!/usr/bin/env python3
"""A known-answer synthetic SciPy calculation, pandas table and rendered figure."""

import argparse
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from scipy import stats


def main():
    module = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, default=module / "outputs")
    args = parser.parse_args()
    values = pd.read_csv(module / "input.csv")["value"].to_numpy(dtype=float)
    if values.shape != (5,) or not np.isfinite(values).all():
        raise ValueError("This known-answer fixture requires five finite observations")
    test = stats.ttest_1samp(values, popmean=0.0)
    interval = test.confidence_interval(confidence_level=0.95)
    table = pd.DataFrame([dict(
        n=values.size, mean=np.mean(values), sd=np.std(values, ddof=1),
        t=test.statistic, df=test.df, p=test.pvalue,
        ci_low=interval.low, ci_high=interval.high,
    )])
    outputs = args.output_directory
    outputs.mkdir(parents=True, exist_ok=True)
    table.to_csv(outputs / "statistics.tsv", sep="\t", index=False, float_format="%.12g")
    plt.rcParams.update({"svg.hashsalt": "datalad-annex-toy-v1", "font.size": 11})
    figure, axis = plt.subplots(figsize=(6, 3.6), layout="constrained")
    axis.plot(np.arange(1, values.size + 1), values, "o", color="#1d6996", label="Input")
    axis.axhline(values.mean(), color="#d97706", label="Sample mean")
    axis.axhspan(interval.low, interval.high, color="#d97706", alpha=0.12,
                 label="95% t interval for mean")
    axis.set(xlabel="Synthetic observation", ylabel="Value (arbitrary units)",
             title="Known-answer workflow fixture", xticks=np.arange(1, 6), ylim=(0, 6))
    axis.legend(loc="upper left", fontsize=9)
    figure.savefig(outputs / "figure.svg", metadata={"Date": None})
    figure.savefig(outputs / "figure.png", dpi=160)
    plt.close(figure)
    print(json.dumps(dict(python=sys.executable, numpy=np.__version__, scipy=scipy.__version__,
                          pandas=pd.__version__, matplotlib=matplotlib.__version__,
                          output=str(outputs), scope="synthetic integration fixture")))


if __name__ == "__main__":
    main()
