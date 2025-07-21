--- Test if player has a pet. Make them one if not.
local petmob = getpet(ch)
if petmob == nil then
   say("You don't have a pet!")
   say("Let's get you a squirrel!")
   petmob = mload("tol-20")
   addpet(ch,petmob)
else
   say("Your pet is " .. petmob.name)
end
