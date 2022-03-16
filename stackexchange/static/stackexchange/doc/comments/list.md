Gets all the comments on the site.

If you're filtering for interesting comments (by score, creation date, etc.) make use of the sort parameter with
appropriate min and max values.

If you're looking to query conversations between users, instead use the /users/{ids}/mentioned and
/users/{ids}/comments/{toid} methods.

The sorts accepted by this method operate on the following fields of the [comment object](#model-Comment):

**creation**
`creation_date`

**votes**
`score`

`creation` is the default sort.

It is possible to create moderately complex queries using `sort`, `min`, `max`, `fromdate`, and `todate`.

This method returns a list of [comments](#model-Comment).
