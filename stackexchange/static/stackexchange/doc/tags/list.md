Returns the tags found on a site.

The `inname` parameter lets a consumer filter down to tags that contain a certain substring. For example, `inname=own`
would return both "download" and "owner" amongst others.

This method returns a list of [tags](#model-Tag).

The sorts accepted by this method operate on the following fields of the tag object:

**popular**
`count`

**name**
`name`

`popular` is the default sort.

It is possible to create moderately complex queries using `sort`, `min`, `max`, `fromdate`, and `todate`.
