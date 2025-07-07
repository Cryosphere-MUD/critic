local o1

local room = getobj(o1, "!route")
local child

while room and not getflag(room, flag.Room) do
  child = room
  room = owner(child)
end

if room then
  obj.interpret(o1, "route "..room.id)
end

if room==owner(o1) then
  obj.interpret(o1, "file_plan !postroute")
else
  obj.interpret(o1, "file_plan !doroute")
end
