local zch = nil
local wch = nil

if random(2)>0 then
  zch = "?"
end

if zch then
  local ch = zch.." and "
end

if zch or wch then
  local ch = zch.." and "
end