--- Move the character from a "push button" trigger

--- Trigger on room:
--- 
--- Trigger Type Program       Phrase             Actor
--- ============ ============= ==================== ==============
--- Command      tol-49        push button

send(ch,"Ooops, you shouldn't have done that!")
movechar(ch,"aylor-2")

--- Alternative version:
--- If something could make the player move rooms before this code is reached
--- you may need to make sure they're still in the room.
---
--- Remember that 'room' is always the room the prog fired in.
---
if ch.room.key == room.key then
   send(ch,"Ooops, you shouldn't have done that!")
   movechar(ch,"aylor-2")
end
