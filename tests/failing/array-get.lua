local docks = {"level1_1", "level1_2", "level1_3", "level1_0"}
for i=1,4 do
        local dock = get(docks[i])
        dock:send("hello")
end