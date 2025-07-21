--- Only one person can pass at a time.
 if ally(ch) then
    say ("Hi " .. ch.name .. "! Please help defend us!")
 else 
    say ("Go away mean old raider!")
    killsee(ch)
 end