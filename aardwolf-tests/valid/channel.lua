--- Part of academy lesson on auction. Is skipped is CH already has auction on.
 if not(channel(ch,"auction")) then 
   sayto(ch,"I see that you have the auction channel turned off "..ch.name..".")
   sayto(ch,"I am going to turn your auction channel on so that we can continue this lesson.")
   sayto(ch,"Feel free to turn it off when we are done.")
   echoat(ch,"")
   channel(ch,"auction","on")
end