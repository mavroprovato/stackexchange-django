Get questions which link to those questions identified in {ids}.

This method only considers questions that are linked within a site, and will never return questions from another Stack
Exchange site.

A question is considered "linked" when it explicitly includes a hyperlink to another question. There are no other
heuristics.

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

It is possible to [create moderately complex queries](#complex-queries) using `sort`, `min`, `max`, `fromdate`, and
`todate`.

This method returns a list of [questions](#model-Question).
