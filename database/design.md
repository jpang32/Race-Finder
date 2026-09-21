### Database Design Approach
Tables:
- location
- race

Locations will be defined by nested territories (country -> state -> county -> town, for example).
The initial reason for splitting this up was because the location can be split differently within different
countries (for esample, certain countries have "territories", some "provinces", others "counties")

On second thought though, it is possible that these might be merged back into the main "race" table: the functionality
for this table would only be apparent when adding more complex features (e.g., searching for races within a certain
radius of a city). We likely will therefore just keep all locations within each row of the race table until it becomes
apparent that we might need to split it up.

For the race table, it was considered calling this "event" and keeping a separate "race" table which stored the distance
and race for each event. This was reconsidered and eventually merged into the main race table for the following reasons:
1. The main aspects of a "race" being tracked are type (swim, bike, run, etc.) and distance, which are not difficult to
track in a generalized table by adding 3 addditional columns (segments, distances, race_type)
2. Keeping a "race_id" foreign key in the event table requires an avoidable JOIN.
3. Keeping a list of distances lets you more easily configure the distances for certain races instead of needing
to add a new entry to the race table.

