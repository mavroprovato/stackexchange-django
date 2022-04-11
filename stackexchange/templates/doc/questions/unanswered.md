Return questions the site considers to be unanswered.

Note that just because a question has an answer, that does not mean it is considered answered. While the rules are
subject to change, at this time a question must have at least one upvoted answer to be considered answered.

To constrain questions returned to those with a set of tags, use the `tagged` parameter with a semi-colon delimited list
of tags. This is an **and** contraint, passing `tagged=c;java` will return only those questions with both tags. As such,
passing more than 5 tags will always return zero results.

Compare with [/questions/no-answers](#/questions/questions_no_answers_list).

This method corresponds roughly with the unanswered tab.

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
