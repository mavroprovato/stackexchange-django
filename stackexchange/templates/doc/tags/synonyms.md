Returns all tag synonyms found on the site.

When searching for synonyms of specific tags, it is better to use [/tags/{tags}/synonyms](#) over this method.

The sorts accepted by this method operate on the following fields of the [tag_synonym object](#model-TagSynonym):

**creation**
`creation_date`

**applied**
`applied_count`

**activity**
`last_applied_date`

`creation` is the default sort.

It is possible to [create moderately complex queries](#complex-queries) using `sort`, `min`, `max`, `fromdate`, and
`todate`.

This method returns a list of [tag_synonyms](#model-TagSynonym).
