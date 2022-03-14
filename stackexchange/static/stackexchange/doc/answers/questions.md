Returns the questions that answers identied by {ids} are on.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `answer_id` on
[`answer`](#model-Answer) objects.

The sorts accepted by this method operate on the following fields of the question object:

**activity**
`last_activity_date`

**creation**
`creation_date`

**votes**
`score`

`activity` is the default sort.

It is possible to create moderately complex queries using `sort`, `min`, `max`, `fromdate`, and `todate`.

This method returns a list of [`questions`](#model-Question).
