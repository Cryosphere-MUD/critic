local face = getobj(o1,"!facing")

local exits={}
local exitcount=0
local curindex=0
local exitname=nil
local oppname=nil

if not exitname then 
  exitname=getstr(face,"short")
end

local f = "the "..exitname
