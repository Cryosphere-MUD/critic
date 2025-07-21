--- Select a random player, inform the room and the target.
local rchar = randchar(LP_PLRONLY)
--- If this were a room prog, we would use:
---    local rchar = randchar(nil, room)

--- If we didn't find anyone, bail.
if rchar == nil then return end

--- Note how with rchar passed to echo as the 'about' char, 
--- it becomes the base char for $N/$S/etc variables.
echo("$n has picked $N as $s target!",rchar)

--- Now send a message to the character themselves.
echoat(rchar,"Congratulations, you're the lucky target!")