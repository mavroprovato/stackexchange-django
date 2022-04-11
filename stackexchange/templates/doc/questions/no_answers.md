Return questions which have received no answers.

Compare with [/questions/unanswered](##/questions/questions_unanswered_list) which merely returns questions that the
sites consider insufficiently well answered.

This method corresponds roughly with this site tab.

To constrain questions returned to those with a set of tags, use the tagged parameter with a semicolon delimited list of
tags. This is an **and** constraint, passing `tagged=c;java` will return only those questions with both tags. As such,
passing more than 5 tags will always return zero results.

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
