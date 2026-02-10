local a = ships.get_docked("level1_1")

local co=getobj(a,"owner")

if not co then
  co=getstr(a,"owner")
  if co then
        co="^rnull location^n".." ("..co..")"
  end
end
