if (self.roomkey == "legend-6") then
   say ("Howdy! Welcome to Texas!")
   transfer(ch,"legend-20");
   purgeobj("all",LP_CARRIEDONLY)
   return
end
say ("Sorry, wrong stop, pardner.")
--- Returning item that triggered prog to ch, is simply:
give(obj,ch)
