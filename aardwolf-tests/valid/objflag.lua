--- Is this item humming?
 if objflag(obj,"hum") then
    say("Cool! This item is humming.")
 end
 
 --- Remove rot-death from goal version of callhero portal.
 objflag(obj,"rot-death",0)