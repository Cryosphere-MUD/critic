local simfunc = function(aobj, dobj, rounds, notify_inc)
  local tally = {}

  local showstats = function(forwho)
	local r = tally[forwho].deaths
  end

  showstats(aobj)

  return tally
end

if arg[1] == "evaluate" then

  local opts = ""
  opts = opts.."a"

else
  simfunc()
end
