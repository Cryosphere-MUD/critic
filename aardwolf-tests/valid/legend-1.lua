--- Local function for check ticket
local function checkticket(char,objkey,dest) 
   if (carries(ch,objkey)) then
      say ("I see you have a ticket to " .. dest .. ". Well, all aboard!")
      say ("Don't forget to give it to the conductor when you reach 
            your destination.")
      transfer(ch,"legend-3");
      return true
   end
   return false;
end
---
--- Main Prog
---
if not(canseechar(self,ch)) then
   say ("Hey! Who said that?!")
   return
else
   say ("So, you wish to board?")
   if (checkticket(ch,"legend-0","Maine")) then return end
   if (checkticket(ch,"legend-1","Mississippi")) then return end
   if (checkticket(ch,"legend-2","Texas")) then return end
   if (checkticket(ch,"legend-3","West Virginia")) then return end
   say ("But you need a ticket!")
end
