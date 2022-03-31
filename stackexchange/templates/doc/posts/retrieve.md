Fetches a set of posts by ids.

This method is meant for grabbing an object when unsure whether an id identifies a question or an answer. This is most
common with user entered data.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `post_id`, `answer_id`, or
`question_id` on [post](#model-Post), [answer](#model-Answer), and [question](#model-Question) objects
respectively.

The sorts accepted by this method operate on the following fields of the [post object](#model-Post):

**activity**
`last_activity_date`

**creation**
`creation_date`

**votes**
`score`

`activity` is the default sort.

It is possible to [create moderately complex queries](#complex-queries) using `sort`, `min`, `max`, `fromdate`, and
`todate`.

This method returns a list of [posts](#model-Post).
