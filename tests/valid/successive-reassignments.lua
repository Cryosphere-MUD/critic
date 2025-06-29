local pl, o1, o2
local midsect = getobj(o1,"grapple.midsection")
local top = getobj(o1,"grapple.top")
local midrope = nil
local toprope = nil

if getstate(o1)==3 then
  midrope=make.clone(get("defence_rope_2"),top)
  setstate(midrope,2)
end

if midsect then
  midrope=make.clone(get("defence_rope_2"),midsect)
  open(midrope)
end

