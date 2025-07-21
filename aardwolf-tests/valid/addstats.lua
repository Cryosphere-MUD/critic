--- Used in academy, small skeleton loads skeleton bone at death with 
--- 2 random stats and random hp between 10 and 30.
local tobj = oload("academy-36")
addstats(tobj,"random",2)
addstats(tobj,"hp",math.random(10,30))

--- Also, rarely, add two more random stats.
if math.random(1,60) == 3 then
   addstats(tobj,"random",2)
end