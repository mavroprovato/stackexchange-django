Returns the privileges a user has.

Applications are encouraged to calculate privileges themselves, without repeated queries to this method. A simple check
against the results returned by /privileges and `user.user_type` would be sufficient.

`{id}` can contain only a single, to find it programmatically look for `user_id` on [user objects](#model-User).

This method returns a list of [privileges](#model-UserPrivilege).
