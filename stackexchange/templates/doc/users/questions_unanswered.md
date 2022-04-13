Gets the questions asked by the users in {ids} which the site considers unanswered, while still having at least one
answer posted.

These rules are subject to change, but currently any question without at least one upvoted or accepted answer is
considered unanswered.

To get the set of questions that a user probably considers unanswered, the returned questions should be unioned with
those returned by /users/{id}/questions/no-answers. These methods are distinct so that truly unanswered (that is, zero
posted answers) questions can be easily separated from merely poorly or inadequately answered ones.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `user_id` on
[user objects](#model-User).

The sorts accepted by this method operate on the following fields of the [question object](#model-Question):

**activity**
`last_activity_date`

**creation**
`creation_date`

**votes**
`score`

`activity` is the default sort.

It is possible to [create moderately complex queries](#complex-queries) using `sort`, `min`, `max`, `fromdate`, and
`todate`.

This method returns a list of [questions](#model-Question).
