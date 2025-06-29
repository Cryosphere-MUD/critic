local a = nil

local f = function()
        print(a)
        a:send("hello")
end

a = get("level2_36")
f()