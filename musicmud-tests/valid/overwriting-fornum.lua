local obj

  for i,v in pairs(obj) do
    if is_valid_object(v) then
      for i,v in pairs(getprops(v, "short_desc")) do
          print(v)
      end
    end
  end