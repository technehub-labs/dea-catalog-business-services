# Shard `v`

CR-SVC-016 bucket for record slugs starting with `v`. The shard
key is the first character of the record's slug (the id minus the
`services:service-` prefix and the `-<hash>` suffix); digit-leading
slugs live in `0-9/`. The path stays derivable from the id alone
(entity-storage-layout.md §5):
`entities/v1-alpha/<shard>/<slug>-<hash>/<id>.yaml`.
