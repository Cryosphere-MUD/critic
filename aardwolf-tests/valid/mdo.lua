--- Wear the object just given
--- Note the single quotes to make sure all keywords are grouped.
 mdo("wear '" .. obj.keywords.. "'") 
 
 --- if it's level 1, drop/sac it.
 if (obj.level == 1) then
    mdo("drop '" .. obj.keywords .. "'")
    mdo("sacrifice '" .. obj.keywords .. "'")
 end
