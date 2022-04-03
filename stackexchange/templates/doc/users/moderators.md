Gets those users on a site who can exercise moderation powers.

Note, employees of Stack Exchange Inc. will be returned if they have been granted moderation powers on a site even if
they have never been appointed or elected explicitly. This method checks abilities, not the manner in which they were
obtained.

The sorts accepted by this method operate on the following fields of the [user object](#model-User):

**reputation**
`reputation`

**creation**
`creation`

**name**
`display_name`

**modified**
`last_modified_date`

`reputation` is the default sort.

It is possible to [create moderately complex queries](#complex-queries) using `sort`, `min`, `max`, `fromdate`, and
`todate`.

This method returns a list of [users](#model-User).
