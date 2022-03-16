Gets the comments on the posts identified in ids, regardless of the type of the posts.

This method is meant for cases when you are unsure of the type of the post id provided. Generally, this would be due to
obtaining the post id directly from a user.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `post_id`, `answer_id`, or
`question_id` on [post](#model-Post), [answer](#model-Answer), and [question](#model-Question) objects respectively.

The sorts accepted by this method operate on the following fields of the [comment object](#model-Comment):

**creation**
`creation_date`

**votes**
`score`

`creation` is the default sort.

It is possible to create moderately complex queries using `sort`, `min`, `max`, `fromdate`, and `todate`.

This method returns a list of [comments](#model-Comment).
