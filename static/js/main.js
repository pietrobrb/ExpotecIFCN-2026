$(window).scroll(function(){
	handleTopNavAnimation();
});

$(window).on('load', function(){
	handleTopNavAnimation();
	smoothScroll.init();
});

function handleTopNavAnimation() {
	var top=$(window).scrollTop();

	if(top>10){
		$('#site-nav').addClass('navbar-solid'); 
	}
	else{
		$('#site-nav').removeClass('navbar-solid'); 
	}
}

/*
 * SmoothScroll
*/
