local arg
local pl

local aarg = "level2_35"
local barg = "level2_36"

local a = mud.match(pl,{ "a" })
local b = mud.match(pl,{ "b" })
      
if a and #a > 0 then a = a[1] else a = nil end
if b and #b > 0 then b = b[1] else b = nil end
      
print(a)

if not a then
        a = get(aarg)
end
if not b then
        b = get(barg)
end

print(a)

if a:person() or b:person() then
        pl:send("Use ^Wconsider^n on people.")
        return
end
      