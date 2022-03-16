Returns the questions identified in {ids}.

This is most useful for fetching fresh data when maintaining a cache of question ids, or polling for changes.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `question_id` on
[question objects](#model-Question).

The sorts accepted by this method operate on the following fields of the [question object](#model-Question):

**activity**
`last_activity_date`

**creation**
`creation_date`

**votes**
`score`

`activity` is the default sort.

It is possible to create moderately complex queries using `sort`, `min`, `max`, `fromdate`, and `todate`.

This method returns a list of [questions](#model-Question).
