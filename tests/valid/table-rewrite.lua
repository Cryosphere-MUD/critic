local pl = get("level1_1")

local targ = mud.match(pl,{"arg"})
if not targ then
  targ = pl
  print(targ)
else
  targ = targ[1]
  print(targ)
end

print(targ)

if not targ then
  return 1
end

print(targ)

getintd(targ,"rant.count",nil)
