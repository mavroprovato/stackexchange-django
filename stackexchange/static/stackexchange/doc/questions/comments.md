Gets the comments on a question.

If you know that you have a question id and need the comments, use this method. If you know you have answer id, use
/answers/{ids}/comments. If you are unsure, use /posts/{ids}/comments.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `question_id` on
[question objects](#model-Question).

The sorts accepted by this method operate on the following fields of the [comment object](#model-Comment):

**creation**
`creation_date`

**votes**
`score`

`creation` is the default sort.

It is possible to create moderately complex queries using `sort`, `min`, `max`, `fromdate`, and `todate`.

This method returns a list of [comments](#model-Comment).
