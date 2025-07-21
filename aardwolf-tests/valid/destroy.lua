--- Lands of Legend prog. Tests if character has all 4 apples, 
--- loads portal (meeting mandatory 1 per area requirement), gives
--- to char, removes the 4 apples from their inventory then 
--- transfers them to Aylor recall.
if carries(ch,"legend-5") and carries(ch,"legend-6") and
   carries(ch,"legend-7") and carries(ch,"legend-37") then
   say("Congratulations! You found my apple trees!")
   local tobj = oload("legend-48")
   give(tobj,ch)
   social("shake",ch)
   destroy(ch,"legend-37")
   destroy(ch,"legend-5")
   destroy(ch,"legend-7")
   destroy(ch,"legend-6")
   echo ("*poof*")
   transfer(ch,"aylor-0")
   return
end