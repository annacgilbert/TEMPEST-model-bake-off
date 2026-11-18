"""Save all manuscript metrics. Refuses to overwrite an existing run directory."""
import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
import numpy as np
import scipy
from numerics import (ROOT, bgk_constants, bgk_theta, variable_bgk_theta,
    dougherty_theta, constants, dougherty, theta, temperatures, landau_matrix,
    kinetic_rollout, moment_rollout, relative_history_error, hermite_response)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(config, output, rebuild=False):
    output.mkdir(parents=True, exist_ok=False)
    start=time.perf_counter()
    cfg=json.loads(Path(config).read_text())
    np.random.seed(cfg['seed'])
    metrics=dict(schema_version=cfg['schema_version'], config=cfg, status='running',
                 uncertainty=dict(ensemble_estimation='not applicable: deterministic',
                    discretization='degree refinement; not a certified continuum bound',
                    learned_model='not applicable: no training'),
                 environment=dict(python=sys.version, executable=sys.executable,
                    numpy=np.__version__, scipy=scipy.__version__,
                    platform=platform.platform(), machine=platform.machine()),
                 input_hashes={}, failures=[], checks={}, landau=[], curves=[], embedded=[])
    out=output/'metrics.json'
    def save():
        metrics['runtime_seconds']=time.perf_counter()-start
        out.write_text(json.dumps(metrics,indent=2,allow_nan=False)+'\n')
    try:
        for name in ('config.json','numerics.py','reproduce.py','test_numerics.py'):
            metrics['input_hashes'][name]=digest(Path(__file__).parent/name)
        for name in ('landau3d.py','closure3d.py'):
            path=ROOT/'shared/scripts/landau_closure'/name
            metrics['input_hashes'][str(path.relative_to(ROOT))]=digest(path)
        tol=cfg['quadrature_relative_tolerance']
        metrics['bgk_constants']={
            'constant':bgk_constants(False,tol), 'variable':bgk_constants(True,tol)}
        metrics['checks']['bgk_independent_resolvent_max_abs']=max(
            abs(bgk_theta(k)-variable_bgk_theta(k,False)[0]) for k in (.1,1,3))
        metrics['checks']['dougherty_hermite_max_abs']=max(
            abs(dougherty_theta(k)-hermite_response(k,100)) for k in (.1,1,3))
        for k in np.geomspace(.0003,100,cfg['curve_points']):
            variable,qerr=variable_bgk_theta(k,True,tol)
            metrics['curves'].append(dict(k=float(k),bgk1=bgk_theta(k,tol),
                variable_bgk1=variable,variable_quadrature_estimate=qerr,
                dougherty1=dougherty_theta(k,1,tol),dougherty3=dougherty_theta(k,3,tol)))
        # Check quadrature tolerance separately from model error.
        metrics['checks']['variable_bgk_tolerance_refinement_max_abs']=max(
            abs(variable_bgk_theta(k,True,tol)[0]-variable_bgk_theta(k,True,tol/10)[0])
            for k in (.001,.01,.1,1,10))
        fresh_start=time.perf_counter()
        _,fresh,chk=landau_matrix(6)
        metrics['checks']['fresh_d6_seconds']=time.perf_counter()-fresh_start
        metrics['checks']['fresh_quadrature_abs_error']=abs(float(chk)-np.sqrt(2/np.pi))
        for degree in cfg['landau_degrees']:
            path=ROOT/f'shared/scripts/landau_closure/cache/landau_d{degree}.npy'
            t0=time.perf_counter()
            origin='fresh'
            if degree==6:
                L=fresh
                if path.exists():
                    metrics['checks']['fresh_vs_cached_d6_max_abs']=float(np.max(abs(L-np.load(path))))
            elif path.exists() and not rebuild:
                L=np.load(path); origin='existing cache'
            else:
                _,L,_=landau_matrix(degree)
            if origin=='existing cache':
                metrics['input_hashes'][str(path.relative_to(ROOT))]=digest(path)
            c={key:float(value) for key,value in constants(L,degree).items()}
            entry=dict(degree=degree, matrix_origin=origin,
                       matrix_seconds=time.perf_counter()-t0,constants=c, responses=[])
            for k in cfg['landau_k']:
                th,n,resmass,resq,X=theta(L,degree,k)
                t=temperatures(L,degree,k)
                entry['responses'].append(dict(k=k,theta=th,ratio=th/k/c['kF'],
                   n=n,X=X,Tperp_over_n=t['Tperp']/t['n1'],
                   minus_T_over_n=-t['T1']/t['n1'],mass_residual=resmass,flux_residual=resq))
            metrics['landau'].append(entry)
            print(f"Landau d={degree}: kappa={c['kF']:.8f}, K={c['Kexact']:.8f}",flush=True)
            save()
        maxeig=[]
        for k in cfg['embedded_k']:
            times=np.linspace(0,cfg['embedded_scaled_final_time']/k,cfg['embedded_samples'])
            refs=[kinetic_rollout(k,d,times) for d in cfg['embedded_degrees']]
            reference,E,q=refs[-1]
            th=dougherty_theta(k)
            chis={'quasistatic':th/k,'fourier':.5,
                  'harmonic':1/(1/.5+k/np.sqrt(2/np.pi))}
            item=dict(k=k,time=times.tolist(),kinetic_T=reference[:,2].real.tolist(),
                numerical_refinement_error=relative_history_error(refs[0][0],reference,times),
                kinetic_energy_max_increase=float(np.max(np.diff(E))),models={})
            for name,chi in chis.items():
                U,F=moment_rollout(k,chi,times)
                item['models'][name]=dict(chi=chi,
                    relative_history_error=relative_history_error(U,reference,times),
                    energy_max_increase=float(np.max(np.diff(F))),
                    initial_flux_error=abs(k*chi),T=U[:,2].real.tolist())
            metrics['embedded'].append(item)
            print(f"Embedded k={k}: refinement={item['numerical_refinement_error']:.2e}",flush=True)
            save()
        metrics['status']='complete'
    except Exception as error:
        metrics['status']='failed'
        metrics['failures'].append(dict(type=type(error).__name__,message=str(error)))
        raise
    finally:
        save()
    print(f"Saved {out}; runtime {metrics['runtime_seconds']:.2f}s",flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--config',default='config.json')
    p.add_argument('--output',required=True)
    p.add_argument('--rebuild-landau',action='store_true')
    args=p.parse_args()
    run(args.config,Path(args.output),args.rebuild_landau)
