Returns the badges that are awarded for participation in specific tags.

For the rank sort, bronze is greater than silver which is greater than gold. Along with `sort=rank`, set `max=gold` for
just gold badges, `max=silver&min=silver` for just silver, and `min=bronze` for just bronze.

`rank` is the default sort.

This method returns a list of [badges](#model-Badge).
