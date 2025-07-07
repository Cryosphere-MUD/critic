local midrope = nil
local pl
local o1

midrope=make.clone(get("defence_rope_2"), owner(o1))
setstate(midrope,2)
set(midrope,"!grapple",getstr(o1,"id"))
set(o1,"!midrope",getstr(midrope,"id"))
