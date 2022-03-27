Returns tag objects representing the tags in {tags} found on the site.

This method diverges from the standard naming patterns to avoid conflicting with existing methods, due to the free form
nature of tag names.

This method returns a list of [tags](#model-Tag).

The sorts accepted by this method operate on the following fields of the [tag object](#model-Tag):

**popular**
`count`

**name**
`name`

`popular` is the default sort.

It is possible to [create moderately complex queries](#complex-queries) using `sort`, `min`, `max`, `fromdate`, and
`todate`.
