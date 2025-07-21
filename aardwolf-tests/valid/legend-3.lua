
if (self.roomkey == "legend-4") then
   say ("OK, we're here. Welcome to Maine!")
   transfer(ch,"legend-10");
   return
end
say ("Sorry, wrong stop.")
--- Returning item that triggered prog to ch, is simply:
give(obj,ch)
