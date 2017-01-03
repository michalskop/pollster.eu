
$dynamicImages = $("[data-src]");

$(window).resize(function() {
    $dynamicImages.each(function(index) {
        if ($(this).css('display') !== 'none') {
            this.src = $(this).data('src');
            //$dynamicImages.splice(index, 1)
        }
    });
}).resize();
