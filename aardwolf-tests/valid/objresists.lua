--- Return number of resistances the item has in fire:
say("Fire resistance on this item is: " .. objresists(obj,FOCUS_FIRE)) -- missing )

--- Increase the number of resistances in Acid by 3
objresists(obj,FOCUS_ACID,3)

--- Reduce resistance in bash by 5
objresists(obj,FOCUS_BASH,-5)

--- Set the item to 100 resists in cold whatever the current value is
local coldres = objresists(obj,FOCUS_COLD)
objresists(obj,FOCUS_COLD,100 - coldres)