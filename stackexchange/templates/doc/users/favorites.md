Get the questions that users in {ids} have bookmarked.

This method is effectively a view onto a user's bookmarks tab, previously known as the "favorites" tab.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `user_id` on
[user](#model-User) objects.

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
