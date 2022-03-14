Returns recently awarded badges in the system, constrained to a certain set of badges.

As these badges have been awarded, they will have the `badge.user` property set.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `badge_id` on
[`badge objects`](#model-Badge).

This method returns a list of [`badges`](#model-Badge).
