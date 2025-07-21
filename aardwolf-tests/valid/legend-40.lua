local roomkey   = self.roomkey
chname = ch.name
if (roomkey == "legend-41") then
   say ("Welcome aboard!")
   say ("Heres your equipment. Hop to it, pal.")
   --- Use the OBJ returned by oload to make sure we give the right item.
   local newobj = oload ("legend-41")
   give(newobj,ch)
   destroy(self,"legend-41")
   social("pat",ch)
   return
end
if (roomkey == "legend-42") then
   say ("Here, can you put this on your head?")
   say ("No? Darn. I'm sober enough to probably hit it.")
   return
end
 
if (roomkey == "legend-43") then
   say ("Once, when I was a child, I wrestled a ten foot catfish.")
   return
end
if (roomkey == "legend-44") then
   say ("Hey, when we get to port, you should come drink with us.")
   say ("It will be fun.")
end
