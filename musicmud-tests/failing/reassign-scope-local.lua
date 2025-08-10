local ql = nil

if o1.blah then
  ql=make.clone(get("template_bag_1"), owner(o1))
  setstate(ql,2)
  set(ql,"!prop",getstr(o1,"id"))
  set(o1,"!ql",getstr(ql,"id"))
end

ql:send("blah")
