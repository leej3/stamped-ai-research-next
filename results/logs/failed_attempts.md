# Retained implementation attempts

- Initial input assertion counted every entry in `sources.json` and failed because the manifest also contains metadata-file entries. The script now selects only participant `*_hypo1_cope.nii.gz` entries and asserts 54.
- First results serialization failed because a voxel-size value remained NumPy float32. The script now converts header zooms to native Python floats.
- A temporary significant-voxel export referenced the NIfTI volume helper before that helper was defined. The export now uses the existing analysis-mask coordinates and runs after ROI construction.

These were analysis-script implementation errors, not changes to the input maps or inferential model. The final successful run is recorded in `group_analysis.log`.
