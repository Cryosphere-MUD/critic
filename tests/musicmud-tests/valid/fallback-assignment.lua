local arg
local pl

local aarg = "level1_1"
local barg = "level1_2"

local a = mud.match(pl,{ "a" })
local b = mud.match(pl,{ "b" })
      
if a and #a > 0 then a = a[1] else a = nil end
if b and #b > 0 then b = b[1] else b = nil end
      
if not a then
        a = get(aarg)
end
if not b then
        b = get(barg)
end

if a:person() or b:person() then
        pl:send("message")
        return
end
      