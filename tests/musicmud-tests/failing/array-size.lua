local a = { "level2_35", "level2_36", "level2_37" }

for c = 1, #a do
        local obj = get(a[c])
        local shop = getobj(obj, "shop.mob")
        send(shop, "hello")
end