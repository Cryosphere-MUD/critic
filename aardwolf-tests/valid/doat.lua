--- Imaginary greet prog to annoy Lasher in multiple ways.
--- warzone-0 is the key of Lasher's imm room.
doat("warzone-0","say Hi Lasher! ")

--- next line could fail if another mob has keyword 'lasher'
doat("lasher","*smile") 

--- Will only target a player. 
doat("lasher","*chuckle",LP_PLRONLY) 