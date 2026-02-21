local target = arg[1]

if target ~= "summary" and target ~= "all" then
        target = get(target)
end

if target == "summary" or target == "all" then
        return
end

print(target.id)