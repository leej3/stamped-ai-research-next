#!/usr/bin/env python3
"""Group analysis of fixed NARPS AO86 participant gain-effect maps."""
from pathlib import Path
import json, hashlib, warnings
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from nilearn import datasets, image, plotting
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'; (OUT/'figures').mkdir(parents=True,exist_ok=True); (OUT/'maps').mkdir(exist_ok=True)
meta=json.loads((ROOT/'input/sources.json').read_text())
participants=pd.read_csv(ROOT/'input/participants.tsv',sep='\t')
files={k:v for k,v in meta['files'].items() if k.endswith('_hypo1_cope.nii.gz')}; assert len(files)==54 and len(participants)==54
ids=participants.participant_id.tolist()
arrs=[]; ref=None; qa=[]
for sid in ids:
    path=ROOT/'input/data'/f'{sid}_hypo1_cope.nii.gz'
    rel=f'data/{sid}_hypo1_cope.nii.gz'
    expected=files[rel]['sha256']
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    checksum_ok=(h.hexdigest()==expected)
    if not checksum_ok: raise RuntimeError(f'SHA256 mismatch for {sid}')
    im=nib.load(str(path)); a=im.get_fdata(dtype=np.float32)
    if ref is None: ref=im
    assert a.shape==ref.shape and np.allclose(im.affine,ref.affine,atol=1e-5),sid
    finite=np.isfinite(a); active=finite & (a!=0)
    qa.append({'participant_id':sid,'sha256_matches_manifest':checksum_ok,'finite_fraction':float(finite.mean()),'nonzero_fraction':float(active.mean()),'nonzero_min':float(a[active].min()),'nonzero_max':float(a[active].max()),'nonzero_mean':float(a[active].mean()),'nonzero_sd':float(a[active].std())})
    arrs.append(a)
Y=np.stack(arrs,axis=0)
# NARPS/participant maps are zero-filled outside each participant's estimated brain coverage.
# Analyze only voxels represented in every map; this gives one fixed, explicit group mask.
coverage=np.sum(Y!=0,axis=0)
mask=coverage==len(ids)
if mask.sum()<1000: # Fallback only if zero coding differs: retain voxels with >=90% coverage.
    mask=coverage>=int(np.ceil(.9*len(ids)))
    warnings.warn('Using >=90% map coverage because complete intersection was too small.')
flat=Y[:,mask]
n=flat.shape[0]; v=flat.shape[1]
means=flat.mean(axis=0); sd=flat.std(axis=0,ddof=1); se=sd/np.sqrt(n)
t=means/se
p_one=stats.t.sf(t,df=n-1) # directional hypothesis, positive gain effect
p_fwe=np.minimum(1,p_one*v) # Bonferroni over all voxels in fixed whole-brain group mask
sig=p_fwe<.05

def volume(values, fill=0.0):
    z=np.full(mask.shape,fill,dtype=np.float32); z[mask]=values.astype(np.float32); return z
hdr=ref.header.copy(); hdr.set_data_dtype(np.float32)
def save_map(name,values):
    nib.save(nib.Nifti1Image(volume(values),ref.affine,hdr),OUT/'maps'/name)
save_map('group_mean_gain_effect.nii.gz',means)
save_map('group_t_positive.nii.gz',t)
save_map('group_p_positive.nii.gz',p_one)
save_map('group_p_fwe_bonferroni.nii.gz',p_fwe)
save_map('group_t_fwe05.nii.gz',np.where(sig,t,0.0))

# Independent vmPFC operationalization: Harvard-Oxford cortical Frontal Medial Cortex
# (25% maximum-probability map), resampled nearest-neighbour to the supplied MNI grid.
atlas=datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm')
lab=list(atlas.labels); matches=[i for i,x in enumerate(lab) if 'Frontal Medial Cortex' in str(x)]
if len(matches)!=1: raise RuntimeError(f'Expected one frontal medial label; got {matches}, {lab}')
roi_img=image.resample_to_img(atlas.maps,ref,interpolation='nearest')
roi=(roi_img.get_fdata()==matches[0]) & mask
if not roi.any(): raise RuntimeError('Empty frontal medial ROI intersection')
roi_beta=Y[:,roi].mean(axis=1)
roi_m=float(roi_beta.mean()); roi_sd=float(roi_beta.std(ddof=1)); roi_se=roi_sd/np.sqrt(n)
roi_t=float(roi_m/roi_se); roi_p=float(stats.t.sf(roi_t,n-1)); roi_ci=stats.t.interval(.95,n-1,loc=roi_m,scale=roi_se)
coords=np.argwhere(mask)[sig]
if len(coords):
    mni=nib.affines.apply_affine(ref.affine,coords)
    pd.DataFrame({'i':coords[:,0],'j':coords[:,1],'k':coords[:,2],'x_mni_mm':mni[:,0],'y_mni_mm':mni[:,1],'z_mni_mm':mni[:,2],'t':t[sig],'p_fwe_bonferroni':p_fwe[sig],'in_frontal_medial_roi':roi[tuple(coords.T)]}).to_csv(OUT/'significant_voxels.tsv',sep='\t',index=False)
else:
    pd.DataFrame(columns=['i','j','k','x_mni_mm','y_mni_mm','z_mni_mm','t','p_fwe_bonferroni','in_frontal_medial_roi']).to_csv(OUT/'significant_voxels.tsv',sep='\t',index=False)
# ROI is used for anatomical localization and descriptive estimate only; hypothesis inference
# is the whole-brain Bonferroni test above.

# QC summaries and participant-level ROI influence diagnostics.
roi_table=pd.DataFrame({'participant_id':ids,'roi_mean_effect':roi_beta})
roi_table['leave_one_out_mean']= [(roi_beta.sum()-x)/(n-1) for x in roi_beta]
roi_table.to_csv(OUT/'participant_roi_estimates.tsv',sep='\t',index=False)
qadf=pd.DataFrame(qa)
qadf['roi_z']=stats.zscore(roi_beta,ddof=1)
qadf.to_csv(OUT/'map_quality.tsv',sep='\t',index=False)

results={
 'analysis':'one-sample group model of participant-level gain contrast estimates; positive one-sided t test',
 'n_included':n,'n_excluded':0,'grid_shape':list(ref.shape),'voxel_sizes_mm':[float(x) for x in ref.header.get_zooms()[:3]],
 'analysis_mask':'intersection of nonzero voxels across all 54 participant effect maps (fallback >=90% only if intersection <1000 voxels)',
 'mask_voxels':int(v),'mask_volume_ml':float(v*np.prod(ref.header.get_zooms()[:3])/1000),
 'effect_units':'upstream contrast-parameter units; gain regressor centered and variance-normalized before HRF convolution, so not per currency unit',
 'whole_brain_correction':'Bonferroni over all voxels in the fixed group mask; directional positive test, familywise alpha=.05',
 'whole_brain_positive_voxels_p_fwe_lt_0_05':int(sig.sum()),
 'whole_brain_minimum_p_fwe':float(p_fwe.min()),'whole_brain_peak_t':float(t.max()),
 'whole_brain_peak_mni_mm':[float(x) for x in nib.affines.apply_affine(ref.affine,np.array(np.unravel_index(np.argmax(volume(t,fill=-np.inf)),mask.shape)))],
 'vmPFC_operationalization':{'atlas':'Harvard-Oxford cortical atlas, max-probability threshold 25%, Frontal Medial Cortex label; resampled nearest neighbor to supplied grid','voxels':int(roi.sum()),'volume_ml':float(roi.sum()*np.prod(ref.header.get_zooms()[:3])/1000),
 'mean_effect':roi_m,'sd_between_participants':roi_sd,'se':roi_se,'t':roi_t,'df':n-1,'one_sided_p_uncorrected_descriptive_only':roi_p,'ci95_t':[float(roi_ci[0]),float(roi_ci[1])],
 'criterion':'support requires at least one positive whole-brain FWE-significant voxel inside this independent anatomical approximation'},
 'support_for_hypothesis':bool(np.any(sig & roi[mask])) if roi.shape==mask.shape else None,
 'mean_voxelwise_effect_in_roi':float(means[np.asarray(roi[mask])].mean()),
 'checks':{'all_maps_same_grid':True,'all_maps_finite':bool(np.isfinite(Y).all()),'all_map_checksums_match':bool(qadf.sha256_matches_manifest.all()),'participants':len(ids),'nonzero_fraction_median':float(qadf.nonzero_fraction.median()),'nonzero_fraction_min':float(qadf.nonzero_fraction.min()),'max_abs_roi_z':float(np.max(np.abs(qadf.roi_z)))},
}
# Correct overlap test support based map voxel coordinates.
roi_flat=roi[mask]
results['support_for_hypothesis']=bool(np.any(sig & roi_flat))
# FWE extrema and mask intersection summaries.
(OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')

# Figure 1: distribution of independent ROI participant estimates.
fig,ax=plt.subplots(figsize=(7.3,4.6))
ax.axhline(0,color='0.4',lw=1)
ax.scatter(np.arange(n)+1,roi_beta,s=25,color='#34699a',alpha=.8,edgecolor='white',linewidth=.3)
ax.axhline(roi_m,color='#b64232',lw=2,label=f'Mean {roi_m:.3f}; 95% CI [{roi_ci[0]:.3f}, {roi_ci[1]:.3f}]')
ax.set(xlabel='Participant (sorted by ID)',ylabel='Frontal medial ROI gain-effect estimate (a.u.)',title='Participant effects in the independent vmPFC approximation')
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(OUT/'figures/roi_participants.png',dpi=180); plt.close(fig)

# Figure 2: whole-brain group t map at uncorrected display threshold; significant corrected voxels outlined through overlays.
# Background template is fetched from Nilearn; display is explicitly descriptive unless FWE mask is shown.
timg=nib.Nifti1Image(volume(t),ref.affine,hdr)
roi_img_show=nib.Nifti1Image(roi.astype(np.uint8),ref.affine,hdr)
fig=plt.figure(figsize=(11,4.6))
disp=plotting.plot_stat_map(timg,bg_img=datasets.load_mni152_template(resolution=2),threshold=2.0,display_mode='z',cut_coords=[-8,0,8,16,24,32],
    cmap='cold_hot',colorbar=True,figure=fig,title='Gain-effect group t map (display threshold |t| > 2; uncorrected)')
disp.add_contours(roi_img_show,levels=[.5],colors='lime',linewidths=1.0)
disp.savefig(OUT/'figures/whole_brain_t.png',dpi=170); plt.close(fig)

# FWE display: only positive voxels surviving Bonferroni, anatomically contextualized.
if sig.any():
    fwe_img=nib.Nifti1Image(volume(np.where(sig,t,0.0),fill=0.0),ref.affine,hdr)
    fig=plt.figure(figsize=(9,4.2))
    disp=plotting.plot_stat_map(fwe_img,bg_img=datasets.load_mni152_template(resolution=2),threshold=0,display_mode='z',cut_coords=[-8,0,8,16,24,32],cmap='hot',colorbar=True,figure=fig,title='Positive gain effect, whole-brain Bonferroni FWE p < .05')
    disp.add_contours(roi_img_show,levels=[.5],colors='cyan',linewidths=1)
    disp.savefig(OUT/'figures/whole_brain_fwe.png',dpi=170); plt.close(fig)
else:
    fig,ax=plt.subplots(figsize=(8,3)); ax.axis('off'); ax.text(.5,.55,'No positive voxel survived whole-brain Bonferroni FWE correction (α = .05).',ha='center',va='center',fontsize=14); ax.text(.5,.35,f'Analysis mask: {v:,} voxels; n = {n}.',ha='center',va='center',fontsize=11); fig.tight_layout(); fig.savefig(OUT/'figures/whole_brain_fwe.png',dpi=180); plt.close(fig)
print(json.dumps(results,indent=2))
