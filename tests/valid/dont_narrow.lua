local argc = #arg

local r1 = get(arg[1])

local patchattr = r1.wild.x..":"..r1.wild.y
local z = r1.wild.z

if not z then
	z = 0
end

if z ~= 0 then
  send(pl, "hello " .. z)
end