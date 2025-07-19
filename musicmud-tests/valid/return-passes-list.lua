local function a()
	return 12, 12
end

local function b()
	return a(), 12
end

local x, y, z = b()
static_assert(x + y + z == 36)