Returns all users on a site.

This method returns a list of [users](#model-User).

The sorts accepted by this method operate on the following fields of the [user object](#model-User):

**reputation**
`reputation`

**creation**
`creation`

**name**
`display_name`

**modified**
`last_modified_date`

`reputation` is the default sort.

It is possible to create moderately complex queries using `sort`, `min`, `max`, `fromdate`, and `todate`.

The inname parameter lets consumers filter the results down to just those users with a certain substring in their
display name. For example, `inname=kevin` will return all users with both users named simply "Kevin" or those with
Kevin as one of (or part of) their names; such as "Kevin Montrose".
