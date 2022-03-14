Gets the comments identified in id.

This method is most useful if you have a cache of comment ids obtained through other means (such as
/questions/{id}/comments) but suspect the data may be stale.

`{ids}` can contain up to 100 semicolon delimited ids. To find ids programmatically look for `comment_id` on
[`comment objects`](#model-Comment).

The sorts accepted by this method operate on the following fields of the [`comment object`](#model-Comment):

**creation**
`creation_date`

**votes**
`score`

`creation` is the default sort.

It is possible to create moderately complex queries using `sort`, `min`, `max`, `fromdate`, and `todate`.

This method returns a list of [`comments`](#model-Comment).
