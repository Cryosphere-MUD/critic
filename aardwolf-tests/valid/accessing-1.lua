if ch.level > 100 then
   send(ch,"You are a noble!")
end

if ch.int < self.int then --- remember, self is the mob running the prog.
   say("I'm smarter than you!")
else
   say("You're smarter than me!")
end