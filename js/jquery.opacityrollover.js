(function(b){var e={mouseOutOpacity:0.67,mouseOverOpacity:1,fadeSpeed:"fast",exemptionSelector:".selected"};b.fn.opacityrollover=function(f){function d(g,h){var c=b(g);if(a.exemptionSelector)c=c.not(a.exemptionSelector);c.fadeTo(a.fadeSpeed,h)}b.extend(this,e,f);var a=this;this.css("opacity",this.mouseOutOpacity).hover(function(){d(this,a.mouseOverOpacity)},function(){d(this,a.mouseOutOpacity)});return this}})(jQuery);