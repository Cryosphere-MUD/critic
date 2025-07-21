--- If lasher is on, send him a debug message.
local tmob = getmob("Lasher",nil,LP_PLRONLY)
if tmob ~= nil then
   send(tmob,"TOL-49 is executing!")
end

--- See if we there's an elite yurgach guard anywhere.
tmob = getmob("elite yurgach huge")
if tmob ~= nil then
   say("There is a huge guard in " .. tmob.roomkey)
end

--- See if there's a forge worker at aylor recall.
--- If not, see if there's one anywhere.
tmob = getmob("aylor-20","aylor-0")
   if tmob ~= nil then
   say("There is an instance of aylor-20 at aylor-0!")
else
   say("There is no aylor-20 in aylor-0")
   tmob = getmob("aylor-20")
   if tmob ~= nil then
      say("But I did find one at " .. tmob.roomkey)
   end
end 