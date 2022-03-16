Gets the badges identified in id.

Note that badge ids are not constant across sites, and thus should be looked up via the
[/badges](#operations-badges-badges_list) method. A badge id on a single site is, however, guaranteed to be stable.

Badge sorts are a tad complicated. For the purposes of sorting (and min/max) `tag_based` is considered to be **greater
than** `named`.

This means that you can get a list of all tag based badges by passing `min=tag_based`, and conversely all the named
badges by passing `max=named`, with `sort=type`.

For ranks, bronze is greater than silver which is greater than gold. Along with `sort=rank`, set `max=gold` for just
gold badges, `max=silver&min=silver` for just silver, and `min=bronze` for just bronze.

`rank` is the default sort.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `badge_id` on
[badge objects](#model-Badge).

This method returns a list of [badges](#model-Badge).
