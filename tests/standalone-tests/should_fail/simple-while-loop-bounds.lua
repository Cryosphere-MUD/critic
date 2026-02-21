local func = function() end

local t = {func}

local i = 1

while i < 5 do
        t[i]()
        i = i + 1
end