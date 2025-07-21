if (self.roomkey == "legend-7") then
   say ("Everything seems in order. Welcome to West Virginia!")
   transfer(ch,"legend-30");
   purgeobj("all",LP_CARRIEDONLY)
   return
end
say ("Sorry, wrong stop.")
--- Returning item that triggered prog to ch, is simply:
give(obj,ch)
