--- Remember where I am, goto aylor recall, purge guards
--- return to start.Not the best example, mob could just
--- use 'doat' if it was converted yet :)
 local chroom = ch.room
 rgoto("aylor-0")
 purgemob("guard") -- XXX
 rgoto(chroom)