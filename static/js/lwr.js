//Add show/hide custom event triggers
$(document).ready(function() {
	$("[name='toggleGold']").bootstrapSwitch({
		onText: "Show Gold",
		offText: "Hide Gold",
		onSwitchChange:function(){
			$(".gold").slideToggle();
		}
	});
	$("[name='toggleGoldOnly']").bootstrapSwitch({
	onText: "Show Only Gold",
	offText: "Hide Only Gold",
	onSwitchChange:function(){
		$(".regular").slideToggle();
	}
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

//Update menu to be active when on part of salient page
$(window).on('scroll', function() {
    $('.anchor').each(function() {
        if($(window).scrollTop() >= $(this).position().top) {
            var name = $(this).attr('name');
            $('.navbar li').removeClass('active');
            $('.navbar a[href=#'+ name +']').parent().addClass('active');
        }
    });
});

//bootstrap switch

;
