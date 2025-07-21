--- Create a portal, give it to the character.
oload("aylor-123")
give("portal",ch)

--- You could also just use:
give(oload("aylor-123"),ch)

--- Oload with no actor.
--- Prog in orchard when user types 'shake tree'
if carries(ch,"orchard-0") then
   send(ch,"You give the tree a good shake, but no apples fall.")
else 
   send(ch,"You give the tree a good shake.nrA shiny red apple falls 
            and you quickly catch it.")
   oload("orchard-0",0,nil,ch)
end