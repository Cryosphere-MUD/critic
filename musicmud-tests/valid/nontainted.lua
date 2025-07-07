local o1

local dest = getobj(o1, "$dest")
local cargo = getobj(o1, "$cargo")
assert(cargo)

if owner(o1)==dest then
  obj.interpret(o1, "put " .. cargo.id .. " on floor")
  setflag(cargo, flag.Fixed, 1)
else
  o1:say("I can't get there! Eek.")
end

local plan = "1 route "..getstr(o1, "home")
print(plan)
plan = plan .. ";1 trap decide"
print(plan)

set(o1, "!plan.!return", plan)
obj.interpret(o1, "file_plan !return")
