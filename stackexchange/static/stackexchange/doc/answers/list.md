Returns all the undeleted answers in the system.

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
