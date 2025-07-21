--- switch weapons if target immune.
if immune(ch,"fire") then -- removed extra )
   mdo("wield ice blade")
end

--- set fire immunity on self
immune(self,"fire","on")

--- remove acid immunity on self
immune(self,"acid","off")