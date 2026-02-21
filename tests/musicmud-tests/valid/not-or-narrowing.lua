local o2 = nil
if random(3) == 2 then
	o2 = get("level1_1")
end

if not o2 or o2.id ~= "level1_2" then return end
