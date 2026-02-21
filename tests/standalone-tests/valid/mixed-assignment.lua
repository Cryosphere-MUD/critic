local function f()
	return 1, 2
end
      
local a, b, c, d = 0, f(), 3

local result = a + b + c + d

static_assert(result == 6)
