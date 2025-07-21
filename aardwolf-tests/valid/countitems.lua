 --- Character must have at least 10 iron ores to continue
 if countitems(ch,"dsr-2") < 10 then
    say("You need at least 10 iron ores for my services!")
    return
 end
 
 --- do whatever in the prog.
 
 --- Now we need to remove them. Can't just use destroy with obj key and all
 --- as they might be carrying more than 10.
 for onum = 1,10,1 do destroy(ch,"dsr-2",LP_SEEALL+LP_ONEONLY) end
