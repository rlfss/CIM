//loading
$(window).on('load',function() {
    $(".loading-overly").fadeOut(1500,
        function () {
            $(this).remove();
            $('body').removeClass('overflow-hidden')
        });
});

// $(function () {
//     $('#datetimepicker1').datetimepicker();
// });

//validation
if($('form').hasClass('validate-fotm')){
    $("#i_form").validate({
        rules: {
            customCheck1: 'required',
            customCheck2: 'required',
            customCheck3: 'required',
            i_password: "required",
            i_c_password: {
                equalTo: "#password"
            }
        },
        messages: {
            customCheck1: 'You must agree to the terms',
            customCheck2: 'You must agree to the terms',
            customCheck3: 'You must agree to the terms',
            i_c_password: {
                equalTo: "Password does not match."
            }
        }
    });
}
$(window).scroll(function () {
    var sticky = $('.sticky'),
        scroll = $(window).scrollTop();

    if (scroll >= 200) {
        sticky.addClass('fixed');
        $('body').addClass('has-fixed');
    }
    else {
        sticky.removeClass('fixed');
        $('body').removeClass('has-fixed');
    }
});
//datepicker
// $('[data-toggle="datepicker"]').datepicker();
$('.custom1').owlCarousel({
    animateOut: 'slideOutDown',
    animateIn: 'zoomInDown',
    items: 1,
    margin: 0,
    stagePadding: 0,
    smartSpeed: 450,
    autoplay: true,
    autoplayTimeout: 5000,
    loop: true,
    autoplayHoverPause: true
});
ScrollReveal().reveal('.reveal', { duration: 1500 });
ScrollReveal().reveal('.dot-list', { duration: 1500 });
ScrollReveal().reveal('.dot-list li', { interval: 300});

