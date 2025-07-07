local out = nil
local out2 = nil
local o2 = get("level2_1")
local r = random(3)

if r == 0 then
  out = "a"
  out2 = "hrm"
elseif r == 1 then
  out = "b"
else
  return
end

o2:say(out2)