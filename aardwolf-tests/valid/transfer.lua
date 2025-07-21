--- Transfer the char that triggered me to Aylor recall
--- even if I can't see them.
transfer(ch,"aylor-0",LP_SEEALL);
--- Transfer all mobs in room to legend-12, and
--- all players to aylor-2. Only transfer players if I can 
--- see them and they're active. Transfer all mobs visible or not.
transfer("all","legend-12",LP_SEEALL+LP_MOBONLY);
transfer("all","aylor-0",LP_PLRONLY+LP_ACTIVEONLY);
