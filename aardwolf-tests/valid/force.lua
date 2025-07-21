--- Force all my guards to wield their sword, this room only
force("aylor-212","wield sword",LP_ALLMOBS+LP_SEEALL+LP_ZONEONLY);

--- Force the player who triggered me to bow.
force(ch,"*bow")

--- Force the player who triggered me and their group to recall.
force(ch,"recall",LP_GROUP)