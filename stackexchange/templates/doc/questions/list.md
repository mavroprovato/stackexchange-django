Gets all the questions on the site.

This method allows you to make fairly flexible queries across the entire corpus of questions on a site. For example,
getting all questions asked in the week of Jan 1st 2011 with scores of 10 or more is a single query with parameters
`sort=votes&min=10&fromdate=1293840000&todate=1294444800`.

To constrain questions returned to those with a set of tags, use the `tagged` parameter with a semicolon delimited list
of tags. This is an **and** constraint, passing `tagged=c;java` will return only those questions with both tags. As
such, passing more than 5 tags will always return zero results.

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
