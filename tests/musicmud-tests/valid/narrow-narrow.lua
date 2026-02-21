local board = nil
local pattern
local subject = nil

if not subject then
      subject = mud.match(pl,{ arg[1] })
      if #subject == 1 then
        subject = subject[1]
      else
        subject = nil
      end
end

print(subject)

if not subject then
        send(pl,"Can't find "..arg[1]..".")
        return
end

if subject:getflag(flag.MissionsBoard) then
        board = subject
end