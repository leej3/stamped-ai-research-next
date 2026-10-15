"""Paired change estimation; result generation uses community packages."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def load_pairs(path):
    frame = pd.read_csv(path, keep_default_na=True)
    if list(frame.columns) != ['participant', 'before', 'after']:
        raise ValueError('Expected participant,before,after schema')
    if len(frame) < 2:
        raise ValueError('At least two complete paired observations are required')
    ids = frame['participant']
    if ids.isna().any() or ids.astype(str).str.strip().eq('').any() or ids.duplicated().any():
        raise ValueError('Participant IDs must be nonempty and unique')
    for column in ['before', 'after']:
        frame[column] = pd.to_numeric(frame[column], errors='raise')
        if not np.isfinite(frame[column].to_numpy()).all():
            raise ValueError('Measurements must be finite with no missing values')
    return frame


def main():
    raw = Path('data/paired.csv')
    frame = load_pairs(raw)
    change = frame['after'].to_numpy() - frame['before'].to_numpy()
    n = len(change)
    mean = float(np.mean(change))
    sd = float(np.std(change, ddof=1))
    se = float(stats.sem(change, ddof=1))
    critical = float(stats.t.ppf(0.975, n - 1))
    summary = {
        'estimand': 'mean within-person change (after minus before)',
        'units': 'arbitrary units', 'n': n, 'excluded': 0, 'df': n - 1,
        'mean_change': mean, 'sample_sd': sd, 'standard_error': se,
        'confidence_level': 0.95, 't_critical': critical,
        'ci_lower': mean - critical * se, 'ci_upper': mean + critical * se,
        'input_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
    }
    out = Path('results')
    out.mkdir(parents=True, exist_ok=True)
    (out/'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True)+'\n')
    frame['change'] = change
    frame.to_csv(out/'changes.csv', index=False)
    plt.rcParams.update({'font.size': 11, 'figure.dpi': 140, 'svg.hashsalt': 'paired-v1'})
    fig, ax = plt.subplots(figsize=(7.5, 4.4), layout='constrained')
    y = np.arange(n)
    ax.scatter(change, y, color='#23687c', s=65, zorder=3, label='Individual paired change')
    ax.errorbar(mean, n+0.7, xerr=critical*se, fmt='D', color='#b74d24',
                markersize=7, capsize=6, linewidth=2, label='Mean and 95% t CI (df = 4)')
    ax.axvline(0, color='#666666', linewidth=1, linestyle='--')
    ax.axhline(n-0.3, color='#dddddd', linewidth=1)
    ax.set_yticks([*y, n+0.7], [*frame['participant'], 'Mean'])
    ax.invert_yaxis()
    ax.set_xlim(-0.25, 3.45)
    ax.set_xlabel('Within-person change: after − before (arbitrary units)')
    ax.set_ylabel('Participant')
    ax.set_title('Synthetic paired experiment: all five changes are positive', loc='left', pad=15)
    ax.text(0.98, 0.04, f'Mean {mean:.2f}; 95% CI [{summary["ci_lower"]:.2f}, {summary["ci_upper"]:.2f}]',
            transform=ax.transAxes, ha='right', va='bottom', color='#b74d24')
    ax.grid(axis='x', alpha=0.2)
    ax.spines[['top', 'right']].set_visible(False)
    fig.savefig(out/'paired-change.png', metadata={'Software': 'Matplotlib'})
    fig.savefig(out/'paired-change.svg', metadata={'Date': None, 'Creator': 'Matplotlib'})
    plt.close(fig)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f'Generated results with NumPy {np.__version__}, SciPy {scipy.__version__}, '
          f'Pandas {pd.__version__}, Matplotlib {matplotlib.__version__}')


if __name__ == '__main__':
    main()
