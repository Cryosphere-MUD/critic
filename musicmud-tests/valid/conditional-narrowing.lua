local subject = nil

if subject and mud.privs(subject) < 12 then
    return
end
