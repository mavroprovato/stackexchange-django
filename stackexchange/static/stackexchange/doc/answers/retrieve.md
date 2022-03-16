
Gets the set of answers identified by ids.

This is meant for batch fetching of questions. A useful trick to poll for updates is to sort by activity, with a minimum
date of the last time you polled.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `answer_id` on
[answer objects](#model-Answer).

The sorts accepted by this method operate on the following fields of the [answer object](#model-Answer):

**activity**
`last_activity_date`

**creation**
`creation_date`

**votes**
`score`

`activity` is the default sort.

It is possible to create moderately complex queries using `sort`, `min`, `max`, `fromdate`, and `todate`.

This method returns a list of [answers](#model-Answer).
