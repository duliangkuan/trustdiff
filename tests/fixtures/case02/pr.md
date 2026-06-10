# fix: include the last partial page in pagination

A customer reported that the final page of results was being dropped when
the total item count was not an exact multiple of the page size. For
example, with 7 records and a page size of 5, page 2 (which should hold the
last 2 records) came back empty.

The root cause was `page_count` using floor division and `get_page`
therefore treating the trailing partial page as out of range.

This PR switches `page_count` to `math.ceil` so a partial trailing page
counts as a real page, and `get_page` now serves it. I added a
`test_partial_last_page` case covering the 7-records / page-size-5 boundary,
plus an extra `page_count` assertion for the partial case.
