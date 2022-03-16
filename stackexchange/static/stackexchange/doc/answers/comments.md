Gets the comments on a set of answers.

If you know that you have an answer id and need the comments, use this method. If you know you have a question id, use
/questions/{id}/comments. If you are unsure, use /posts/{id}/comments.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `answer_id` on
[answer objects](#model-Answer).

The sorts accepted by this method operate on the following fields of the [comment object](#model-Comment):

**creation**
`creation_date`

**votes**
`score`

`creation` is the default sort.

It is possible to [create moderately complex queries](#complex-queries) using `sort`, `min`, `max`, `fromdate`, and
`todate`.

This method returns a list of [comments](#model-Comment).
