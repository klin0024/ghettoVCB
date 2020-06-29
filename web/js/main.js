laydate.render({
  elem: '#date' 
});

$( "#submit" ).click(function() {
   var date=$( "#date" ).val();
   loadhtml(servers,date)
});


var date=$.format.date(new Date(), 'yyyy-MM-dd')
$( "#date" ).val(date);

loadhtml(servers,date);

