Returns edit revisions for the posts identified in ids.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `post_id`, `answer_id`, or
`question_id` on [post](#model-Post), [answer](#model-Answer), and [question](#model-Question) objects
respectively.

This method returns a list of [revisions](#model-PostRevision).
