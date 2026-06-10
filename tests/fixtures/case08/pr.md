# refactor: extract helpers in parse_config

`parse_config` had grown into a single loop body doing three things at once
(skip detection, splitting, assignment). This PR pulls out two small private
helpers — `_is_skippable` for blank/comment lines and `_split_pair` for the
`key=value` split — and renames the loop locals to be clearer (`stripped`,
`pair`).

Pure refactor: the public `parse_config` signature and behavior are
unchanged, so the existing tests are left exactly as-is and still pass.
