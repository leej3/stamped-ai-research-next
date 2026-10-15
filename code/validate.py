"""Independent known-input and analytic-oracle checks, with contract negatives."""
from pathlib import Path
from fractions import Fraction
import hashlib
import io
import json
import math
import tempfile
import pandas as pd
from scipy import stats
from analyze import load_pairs


def main():
    frame = load_pairs('data/paired.csv')
    known = [('A',10,11), ('B',20,21), ('C',30,32), ('D',40,42), ('E',50,53)]
    assert list(frame.itertuples(index=False, name=None)) == known
    expected_changes = [1, 1, 2, 2, 3]
    # Independent oracle: rational arithmetic on fixed expected differences.
    mean = sum(map(Fraction, expected_changes)) / 5
    ss = sum((Fraction(x)-mean)**2 for x in expected_changes)
    variance = ss / 4
    assert (mean, ss, variance) == (Fraction(9,5), Fraction(14,5), Fraction(7,10))
    se = math.sqrt(float(variance / 5))
    critical = 2.7764451051977987
    expected = {'n':5, 'excluded':0, 'df':4, 'mean_change':float(mean),
                'sample_sd':math.sqrt(float(variance)), 'standard_error':se,
                'confidence_level':0.95, 't_critical':critical,
                'ci_lower':float(mean)-critical*se, 'ci_upper':float(mean)+critical*se}
    got = json.loads(Path('results/summary.json').read_text())
    for key,value in expected.items():
        assert math.isclose(got[key], value, rel_tol=0, abs_tol=1e-12), (key,got[key],value)
    assert got['input_sha256'] == hashlib.sha256(Path('data/paired.csv').read_bytes()).hexdigest()
    assert got['units'] == 'arbitrary units'
    assert got['estimand'] == 'mean within-person change (after minus before)'
    direct = stats.ttest_rel(frame['after'], frame['before']).confidence_interval(0.95)
    assert math.isclose(got['ci_lower'], direct.low, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(got['ci_upper'], direct.high, rel_tol=0, abs_tol=1e-12)
    changes = pd.read_csv('results/changes.csv')
    assert list(changes.columns) == ['participant','before','after','change']
    assert changes['participant'].tolist() == list('ABCDE')
    assert changes['change'].tolist() == expected_changes
    for c in ['before', 'after']:
        assert changes[c].tolist() == frame[c].tolist()
    invalid = {
        'duplicate_id': 'participant,before,after\nA,1,2\nA,2,3\n',
        'missing_id': 'participant,before,after\n,1,2\nB,2,3\n',
        'missing_value': 'participant,before,after\nA,1,NA\nB,2,3\n',
        'nonfinite': 'participant,before,after\nA,1,inf\nB,2,3\n',
        'nonnumeric': 'participant,before,after\nA,1,nope\nB,2,3\n',
        'singleton': 'participant,before,after\nA,1,2\n',
        'wrong_schema': 'participant,after,before\nA,2,1\nB,3,2\n',
    }
    checked=[]
    with tempfile.TemporaryDirectory() as tmp:
        for name,content in invalid.items():
            path=Path(tmp)/f'{name}.csv';path.write_text(content)
            try: load_pairs(path)
            except (ValueError, TypeError): checked.append(name)
            else: raise AssertionError(f'Invalid input accepted: {name}')
    result={'status':'passed', 'actual_input_rows':5, 'missing':0, 'excluded':0,
            'expected_changes':expected_changes, 'analytic_oracle':expected,
            'tolerance_absolute':1e-12, 'independent_scipy_paired_ci':[float(direct.low),float(direct.high)],
            'rejected_cases':checked}
    Path('results/validation.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__ == '__main__':main()
