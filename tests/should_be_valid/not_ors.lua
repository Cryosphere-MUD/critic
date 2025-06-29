local a, b = get("@a"), get("@b")

if not a or not b then
else
  a:send("hello")
  b:send("hello")
end
