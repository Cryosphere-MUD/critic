
if (self.roomkey == "legend-5") then
   say ("OK, we're here. Is this the first time you've seen the 
         Muddy Mississippi?")
   transfer(ch,"legend-40");
   return
end
say ("Sorry, wrong stop.")
--- Returning item that triggered prog to ch, is simply:
give(obj,ch)
