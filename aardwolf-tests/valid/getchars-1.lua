--- List all chars in the room and send a msg to the players only.
local chars = getchars(room.key)
for k, v in pairs(chars) do
   say("I see " .. v.name .. " in the room.")
   if isplayer(v) then
       send(v,"Hi " .. v.name .. " you appear to be a player!")
   end
end