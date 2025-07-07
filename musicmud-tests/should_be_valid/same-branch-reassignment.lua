local target = nil

local world = mud.match(pl, arg)

if true then
  target = get("level2_36")
  target = getstr(target, "short")
end

print(target)

if target==nil then
  target = arg[1]
end

print(target)

string.lower(target)

