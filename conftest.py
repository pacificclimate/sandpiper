import collections
import collections.abc

# restore the old names so ce.api.geo can import them
collections.Set = collections.abc.Set
collections.Mapping = collections.abc.Mapping
