local targ = self.target -- changed to local as critic dislikes globals

if targ == nil then
   say ("I don't have a target")
   remember(ch)
else
   if (targ.gid == ch.gid) then
      say ("Hi! You're my target!")
   else
      say ("My target's name is " .. targ.name)
   end
end