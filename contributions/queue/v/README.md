# Queue shard `v`

CR-SVC-016 bucket for intake submissions whose slug starts with
`v`; digit-leading slugs live in `0-9/`. The queue gate
(`scripts/check_contributions.py`) and the admission tool
(`scripts/admit_entity.py`) resolve the shard from the filename, so the
intake path stays derivable from the submission slug alone.
