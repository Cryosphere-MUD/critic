local a = nil

local f = function()
        print(a)
        a:send("hello")
end

f()