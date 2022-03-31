Gets the answers to a set of questions identified in id.

This method is most useful if you have a set of interesting questions, and you wish to obtain all of their answers at
once or if you are polling for new or updates answers (in conjunction with sort=activity).

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `question_id` on
[question objects](#model-Question).

The sorts accepted by this method operate on the following fields of the [answer object](#model-Answer):

**activity**
`last_activity_date`

**creation**
`creation_date`

**votes**
`score`

`activity` is the default sort.

It is possible to [create moderately complex queries](#complex-queries) using `sort`, `min`, `max`, `fromdate`, and
`todate`.

This method returns a list of [answers](#model-Answer).
