Gets the users identified in ids in {ids}.

Typically, this method will be called to fetch user profiles when you have obtained user ids from some other source,
such as /questions.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `user_id` on
[user objects](#model-User).

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
