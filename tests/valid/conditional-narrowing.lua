local subject = nil
local mobj = nil

if subject and mud.privs(subject) < mud.minlevel(mobj) then
    return
end
