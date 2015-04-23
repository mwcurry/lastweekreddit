//Add show/hide custom event triggers
$(document).ready(function() {
	$(".hideGold").click(function() {
		$(".gold").slideToggle();
		$(this).toggleClass("glyphicon glyphicon-ok");
	});
});

$(document).ready(function() {
	$(".onlyGold").click(function() {
		$(".regular").slideToggle();
		$(this).toggleClass("glyphicon glyphicon-ok");
	});
});

//Javascript to expand thanks to Diego F.
$(document).ready(function(e) {
	$("a.expand").click(function(e){
	  var excerpt = $(e.target).parents(".item").find("p.excerpt");
	  var link = $(e.target);
	  if (excerpt.hasClass("truncate")) {
	    excerpt.removeClass("truncate");
	    link.html("Close")
	  	}
	  else {
	    excerpt.addClass("truncate");
	    link.html("Expand")
	  	}
	  });
});