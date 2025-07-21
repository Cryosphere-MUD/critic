--- If there is an instance of aylor-123 in the room, the player 
--- may proceed north (pressure pads?)
--- Exit trigger for north.
local tobj = getobj("aylor-123",room,0)
if tobj ~= nil then
   transfer(ch,"roomkey-1")
end

--- See if the gem has been placed in the statue in the room.
--- Assume statue is key test-2 and the gem is test-3

--- Make sure the statue is still here, just in case
local statue = getobj("test-2",room,0)
if statue ~= nil then
   --- Is the gem inside it?
   local gem = getobj("test-3",statue,0)
   if gem ~- nil then
      --- The gem is here ... do something.
   end
end