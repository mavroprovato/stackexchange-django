This is the documentation for the v2.3 Stack Exchange API

## General

Unless otherwise noted, the maximum size of any page is `100`, any `{ids}` parameter likewise is capped at `100`
elements, all indexes start at 1.

It is possible to compose reasonably complex queries against the live Stack Exchange sites using the `min`, `max`,
`fromdate`, `todate`, and `sort` parameters. Most, but not all, methods accept some or all of these parameters, the
documentation for individual methods will highlight which do. Most methods also have a common set of
[paging parameters](#paging).

<div id="vectorized-requests"></div>

## Vectorized Requests

Most methods that take ids in the API will take up to 100 of them in a single go. This allows applications to batch work
and thereby avoid unnecessary round trips, which can be a significant user experience win on slow or high latency
devices. Those methods with different vector limits will mention that in their individual documentation.

When passing a vector, separate each id with a semicolon. For example, [/users/1;2;3;4;5](#operations-users-users_list)
would fetch users with ids 1 through 5.

Vectors are not restricted to integer values, /tags/{tags}/synonyms takes a list of tags (strings) and /revisions/{ids}
takes a list of revision ids (guids).

Note that for caching and throttling purposes, vectors are considered unordered. That is,
[/users/1;2;3](#operations-users-users_list) is semantically identical to [/users/3;2;1](#operations-users-users_list).

<div id="complex-queries"></div>

## Complex Queries

Simple usage of the API focuses around getting large sets of data about sites quickly. It's fairly obvious how to grab
all of a user's answers, even all of a large set of users' via [vectorized requests](#vectorized-requests), all recent
comments, and so on. What's less obvious is how to cull our datasets to smaller chunks of data.

The API provides the `sort`, `min`, `max`, `fromdate`, and `todate` parameters on many methods to allow for more
complicated queries. `min` and `max` specify the range of a field must fall in (that field being specified by sort) to
be returned, while `fromdate` and `todate` always define the range of `creation_date`. Think these parameters as
defining two "windows" in which data must fit to be returned.

`min`, `max`, `fromdate`, and `todate` are inclusive.

<div id="paging"></div>

## Paging

Nearly all methods in the API accept the `page` and `pagesize` parameters for fetching specific pages of results from
the API. `page` starts at and defaults to 1, `pagesize` can be any value between 0 and 100 and defaults to 30.

Since the `{ids}` and similar parameters on methods like [/questions/{ids}](#operations-questions-questions_list) are
constrained to 100 or fewer ids, it is always possible to fetch the entirety of a result from those methods in a single
request (the same does not apply to methods like [/users/{ids}/answers](#operations-users-users_answers_list) since the
ids passed are not answer ids). However, it is sometimes more useful to run "top M of N by X" style queries as with this
most recently active query.
