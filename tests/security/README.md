# Defensive data-safety verification

Source CSV hashes cover all fictional fixture CSVs including the pre-existing untracked snapshot. Compare with `sha256sum -c reports/phase6/evidence/source_before.sha256` from the repository root. Review Git changes to sample-data, workspace write paths, public fixture content and likely credentials. Record findings without copying secret candidate values into evidence.
