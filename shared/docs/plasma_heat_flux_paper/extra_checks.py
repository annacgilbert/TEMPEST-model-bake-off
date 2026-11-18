"""Additional error-budget checks; no existing result file is overwritten."""
import argparse
import json
import time
from pathlib import Path
import numpy as np
from numerics import (ROOT, dougherty, theta, dougherty_theta, kinetic_rollout,
                      moment_rollout, relative_history_error)

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('metrics', type=Path)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--compare-metrics', type=Path)
args=parser.parse_args()
start=time.perf_counter()
target=args.output
if target.exists():
    raise FileExistsError(target)
m=json.loads(args.metrics.read_text())
cfg=m['config']
checks={'metric_sampling_refinement':[], 'landau_cache_symmetry':[],
        'landau_constant_fresh_cache_difference':[],
        'metrics_source':str(args.metrics), 'skipped':[]}
cached={} if args.compare_metrics is None else {
    e['degree']:e for e in json.loads(args.compare_metrics.read_text())['landau']}
for fresh in m['landau']:
    d=fresh['degree']
    cache=ROOT/f'shared/scripts/landau_closure/cache/landau_d{d}.npy'
    if cache.exists():
        L=np.load(cache)
        checks['landau_cache_symmetry'].append({'degree':d,'max_abs':float(np.max(abs(L-L.T)))})
    else:
        checks['skipped'].append(f'Optional cache symmetry: no cache for degree {d}')
    if d in cached:
        checks['landau_constant_fresh_cache_difference'].append({'degree':d,'max_abs':max(
            abs(fresh['constants'][key]-cached[d]['constants'][key]) for key in fresh['constants'])})
checks['dougherty3_stationary_max_abs']=max(abs(theta(dougherty(32),32,k)[0]
    -dougherty_theta(k,3)) for k in (.05,.2,.5,1,2))
for item in m['embedded']:
    k=item['k']
    times=np.linspace(0,cfg['embedded_scaled_final_time']/k,2*cfg['embedded_samples']-1)
    ref,_,_=kinetic_rollout(k,cfg['embedded_degrees'][-1],times)
    row={'k':k,'errors':{}}
    for name,entry in item['models'].items():
        U,_=moment_rollout(k,entry['chi'],times)
        val=relative_history_error(U,ref,times)
        row['errors'][name]={'refined':val,'abs_change':abs(val-entry['relative_history_error'])}
    checks['metric_sampling_refinement'].append(row)
times=np.linspace(0,10,11)
ref,_,_=kinetic_rollout(0,16,times)
checks['kinetic_zero_mode_max_abs_drift']=float(np.max(abs(ref-ref[0])))
U,_=moment_rollout(0,.5,times)
checks['moment_zero_mode_max_abs_drift']=float(np.max(abs(U-U[0])))
checks['max_kinetic_energy_increase']=max(r['kinetic_energy_max_increase'] for r in m['embedded'])
checks['max_moment_energy_increase']=max(v['energy_max_increase'] for r in m['embedded']
                                       for v in r['models'].values())
checks['max_mass_residual']=max(r['mass_residual'] for e in m['landau'] for r in e['responses'])
checks['max_flux_residual']=max(r['flux_residual'] for e in m['landau'] for r in e['responses'])
checks['runtime_seconds']=time.perf_counter()-start
target.parent.mkdir(parents=True,exist_ok=True)
with target.open('x') as stream:
    stream.write(json.dumps(checks,indent=2,allow_nan=False)+'\n')
print(json.dumps(checks,indent=2))
