
function getRandomStr(){
	var rand=Math.floor(Math.random()*1000);
	return rand
}

function load(server,date){

	var rand=getRandomStr();
	htmlfile='servers/'+server+'/'+server+'-'+date+'.html'+'?v='+rand;
		
	$( "#iframe" ).append('<h1 class="text-left"><strong>'+server+'</strong></h1>');
	$( "#iframe" ).append('<table class="table table-hover text-center"><tbody id='+server+'><tr><td><strong>TIME</strong></td><td><strong>SERVER</strong></td><td><strong>VM NAME</strong></td><td><strong>SIZE</strong></td><td><strong>STATUS</strong></td></tr>');
  	$.get(htmlfile,function(data){	
 		$("#"+server).append(data); 
 	});	
	$( "#iframe" ).append('</tbody></table>');
	$( "#iframe" ).append('<br>');
  		
};

function loadhtml(servers,date){

	$( "#iframe" ).html('')
	servers.forEach(function(server) {
		load(server,date)
	});
};

