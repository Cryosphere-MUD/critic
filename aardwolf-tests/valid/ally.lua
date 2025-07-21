--- Only one person can pass at a time.
 if ally(ch) then
    say ("Hi " .. ch.name .. "! Please help defend us!")
 else 
    say ("Go away mean old raider!")
    kill(ch) -- ABI: KILLSEE not documented, changed to kill???
 end