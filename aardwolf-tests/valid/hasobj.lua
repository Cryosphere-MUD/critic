if hasobj(ch,"weapon") then
   say ("Looks like you came ready for a fight?")
   if not(wearsobj(ch,"weapon")) then
      say ("Here's a hint, your weapon will work better wielded!")
   end
end