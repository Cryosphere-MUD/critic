
if obj.level < 100 then
   say ("I don't accept this low level junk!")
   mdo ("give " .. obj.name .. " " .. ch.name)
end