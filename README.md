# ComboFilter

A simple Python script to gather tweets from the Twitter streaming API which are filtered by both `any(keywords)` and a geographical bounding box. As well as storing the keyword-matching tweets, it also maintains a record of the locations of all (i.e. even non-matching) tweets which fall within the bounding box, to allow for tweet-density weighting of result counts.

Configuration is done through a `configparser` config file. See `example.ini` for an outline. Launch with `python combofilter.py`, optionally specifying a configuration file. The tool can also be loaded from within a python shell by instantiating a `FilterListener` object with an appropriate configuration object.

