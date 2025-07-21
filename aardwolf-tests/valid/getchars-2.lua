local chars = getchars(ch.roomkey)
for k,v in pairs(chars) do
  say(v.name)
end

echo("")
say("------ Players Only --------")
local chars = getchars(ch.roomkey,LP_PLRONLY)
for k,v in pairs(chars) do
   say(v.name)
end

echo("")
say("------ Players Only No Imm --------")
local chars = getchars(ch.roomkey,LP_PLRONLY + LP_NOIMM)
for k,v in pairs(chars) do
   say(v.name)
end

echo("")
say("------ Mobs Only --------")
local chars = getchars(ch.roomkey,LP_MOBONLY)
for k,v in pairs(chars) do
   say(v.name)
end

echo("")
echo("Counts....")
say("All Characters: " .. countchars(ch.roomkey))
say("All Players: " .. countchars(ch.roomkey,LP_PLRONLY))
say("All Players (No imms): " .. countchars(ch.roomkey,LP_PLRONLY+LP_NOIMM))
say("Mobs Only: " .. countchars(ch.roomkey,LP_MOBONLY))