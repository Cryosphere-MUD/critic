--- On a greet trigger, ask character to wait in waiting room.
--- If I'm already paused for someone else, do nothing.
if not(hasdelay()) then
   say("Hi " .. ch.name .. ". Wait here please.");
   remember(ch)
   adddelay(10) --- 10 seconds.
end

--- In the delay prog.
targ = self.target
if (targ == nil) {
   --- Target left, how rude.
   social("mutter")
} else {
   say("His lordship will meet you now " .. targ.name);
   mdo("unlock gate");
   mdo("open gate");
}
--- forget existing target.
forget()

--- In seperate prog if character tries to enter without waiting.
say ("Don't be so rude! Now you can just sit and wait!")
cancel()  --- prog that opens door won't fire.