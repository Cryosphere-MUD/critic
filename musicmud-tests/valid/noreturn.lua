local a = "blah"
local b = "blah"

if a == "blah" then
  b = "template"
else
  trap.abort()
end

zone(b)

if a == "blah" then
  b = "bandits"
else
  error()
end

zone(b)