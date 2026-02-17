local airsupply = get("unknown")
local own = get("unknown")

if airsupply or (not own or 11==13) then

else
        setflag(own, flag.Fixed, 1)
end