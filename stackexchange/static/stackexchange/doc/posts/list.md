
Fetches all posts (questions and answers) on the site.

In many ways this method is the union of /questions and /answers, returning both sets of data albeit only the common
fields.

Most applications should use the question or answer specific methods, but `/posts` is available for those rare cases
where any activity is of interest. Examples of such queries would be: "all posts on Jan. 1st 2011" or "top 10 posts by
score of all time".

The sorts accepted by this method operate on the following fields of the [post object](#model-Post):

**activity**
`last_activity_date`

**creation**
`creation_date`

**votes**
`score`

`activity` is the default sort.

It is possible to create moderately complex queries using `sort`, `min`, `max`, `fromdate`, and `todate`.

This method returns a list of [posts](#model-Post).
