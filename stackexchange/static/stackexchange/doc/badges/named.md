Gets all explicitly named badges in the system.

A named badged stands in opposition to a tag-based badge. These are referred to as general badges on the sites
themselves.

For the rank sort, bronze is greater than silver which is greater than gold. Along with `sort=rank`, set `max=gold` for
just gold badges, `max=silver&min=silver` for just silver, and `min=bronze` for just bronze.

`rank` is the default sort.

This method returns a list of [badges](#model-Badge).
