local o1

local cargo = nil
local dest = nil

for i, v in pairs(children(owner(o1))) do
  local d = getobj(v, "cargodest")
  if d ~= nil then
    cargo = v
    dest = d
  end
end


if cargo == nil then
  return
end

print(cargo)

setflag(cargo, flag.Fixed, 0)

obj.interpret(o1, "take " .. cargo.id)
