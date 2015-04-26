//Add show/hide custom event triggers
$(document).ready(function() {
	$("[name='toggleGold']").bootstrapSwitch({
		state: "false",
		size: "small",	
		inverse: "true",
		onColor: "warning",
		onText: "On",
		offText: "Off",
		labelText: "Gold",
		handleWidth: "60",
		onSwitchChange:function(){
			$(".gold").slideToggle();
			$("[name='toggleGoldOnly']").bootstrapSwitch('toggleReadonly');
		}
	});
	$("[name='toggleGoldOnly']").bootstrapSwitch({
		state: "true",
		size: "small",
		inverse: "true",
		onColor: "default",
		offColor: "warning",
		onText: "Off",
		offText: "On",
		labelText: "Gold Only",
		handleWidth: "60",
		onSwitchChange:function(){
			$(".regular").slideToggle();
			$("[name='toggleGold']").bootstrapSwitch('toggleReadonly');
		}
	});
});

$(document).ready(function(){
    $('#modal').modal("show");
    
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
//Todo, repalce with bootstrap spy
$(window).on('scroll', function() {
    $('.anchor').each(function() {
        if($(window).scrollTop() >= $(this).position().top) {
            var name = $(this).attr('name');
            $('.navbar li').removeClass('active');
            $('.navbar a[href=#'+ name +']').parent().addClass('active');
        }
    });
});
