
echo ("Paul makes one final stab at the land in the middle of")
echo ("Round River, digging out the soil there.nr")
say ("There! That should do it. Guess we'll have to call it 
      Round Lake from now on.")
transfer ("all","legend-15",LP_PLRONLY)
rgoto ("legend-14")
if (mobexists("legend-15",room)) then
   purgemob("legend-15",LP_ALLMOBS)
end
if (mobexists("legend-11",room)) then
  purgemob("legend-11",LP_ALLMOBS)
end
if (mobexists("legend-13",room)) then
  purgemob("legend-13",LP_ALLMOBS)
end
if (mobexists("legend-7",room)) then
  purgemob("legend-7",LP_ALLMOBS)
end
