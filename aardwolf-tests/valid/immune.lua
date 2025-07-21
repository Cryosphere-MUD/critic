--- switch weapons if target immune.
if immune(ch,"fire")) then
   mdo("wield ice blade")
end

--- set fire immunity on self
immune(self,"fire","on")

--- remove acid immunity on self
immune(self,"acid","off")