if carries(ch,"legend-5") and carries(ch,"legend-6") and
   carries(ch,"legend-7") and carries(ch,"legend-37") then
   say("Congratulations! You found my apple trees!")
   local newobj = oload("legend-48")
   give(newobj,ch)
   social("shakes",ch)
   destroy(ch,"legend-37")
   destroy(ch,"legend-5")
   destroy(ch,"legend-7")
   destroy(ch,"legend-6")
   echo ("*poof*")
   transfer(ch,"aylor-0",LP_SEEALL)
   return
end

say ("Sorry, you haven't found all my apple trees yet...")
say ("Or did you eat all the apples?")
social("heh")
transfer(ch,"legend-0",LP_SEEALL)
