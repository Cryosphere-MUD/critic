local a = nil

local function f(number)
        if number == 0 then
                return 1
        else
                return f(number - 1 ) * number
        end
end

print(f(12))
