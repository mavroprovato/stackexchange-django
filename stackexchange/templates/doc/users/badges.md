Get the badges the users in {ids} have earned.

Badge sorts are a tad complicated. For the purposes of sorting (and min/max) `tag_based` is considered to be **greater
than** `named`.

This means that you can get a list of all tag based badges a user has by passing `min=tag_based`, and conversely all the
named badges by passing `max=named`, with `sort=type`.

For ranks, bronze is greater than silver which is greater than gold. Along with `sort=rank`, set `max=gold` for just
gold badges, `max=silver&min=silver` for just silver, and `min=bronze` for just bronze.

`rank` is the default sort.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `user_id` on the
[user object](#model-User).

This method returns a list of [badges](#model-Badge).
