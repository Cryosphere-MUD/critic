local desc = "???"

  local startchar, endchar, coloured = string.find(desc,"%^o([%a%d%s]-)%^n")

  while (startchar) do
    startchar, endchar, coloured = string.find(desc,"%^o([%a%d%s]-)%^n", startchar + 1)
  end
