local to
local match = string.find(to,"%u%d")

if match == nil or match > 1 then
	return
end

match = string.find(to,"%u%d")

if not match or match > 1 then
	return
end
