--- Create a mob
local newmob = mload("aylor-20")

--- Use the ch variable for transfer.
transfer(newmob,"aylor-321")

--- Or, if you want to use the newmob in an echo 
--- $n is the mob running the prog. $N is whatever char is given.
echo("$n waves $s arms and $N appears!",newmob)