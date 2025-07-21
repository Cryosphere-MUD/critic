if affected(ch,"flying") then
        say ("Hey, how's the view from up there?")
     elseif affected(ch,"diseased") then
        say ("Ugh, keep away from me please, I don't want to get sick!")
     end
     
     if not(affected(self,"sanctuary")) then
        say ("Uhoh, my sanctuary is down!")
     end