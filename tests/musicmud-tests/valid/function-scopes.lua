local func = function(a, b, c, d)
  local dict = {}

  local showstats = function(e)
	local r = dict[e].prop
  end

  showstats(a)

  return dict
end

if arg[1] == "str" then

  local opts = ""
  opts = opts.."a"

else
  func()
end
