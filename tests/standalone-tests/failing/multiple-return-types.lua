local function f()
  return 1, 2
end

local a, b = f()

static_assert(a + b == 4)