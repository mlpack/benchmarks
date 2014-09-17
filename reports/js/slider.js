$(document).ready(function() {
    return $("a.info").on("click", function(t) {
        var e, n;
        return t.preventDefault(), e = t.target, n = $(e).closest(".collapse-group").find(".infos"), n.collapse("toggle")
    }), $(".graphs").on("click", function(t) {
        var e, n;
        return e = t.target, n = $(e).closest(".collapse-group").find(".graph"), 0 !== n.children("div").length ? (t.stopPropagation(), t.preventDefault(), n.collapse("toggle")) : void 0
    }), $(".memory").on("click", function(t) {
        var e, n;
        return e = t.target, n = $(e).closest(".collapse-group").find(".memories"), 0 !== n.children("div").length ? (t.stopPropagation(), t.preventDefault(), n.collapse("toggle")) : void 0
    }), $(".collapse").on("show", function(t) {
        return $(t.target).removeClass("collapsed")
    }), $(".collapse").on("hidden", function(t) {
        return $(t.target).addClass("collapsed")
    }), $(".all-graphs").on("click", function(t) {
        return $(document).find(".graph").click(), t.preventDefault()
    }), $(".chart").on("click", function(t) {
        if (!$(t.target).hasClass('m')) {
            var target = t.target.id
            var ids = target.split(",");
            for (var i = 0; i < ids.length; i++) {
                loadScript(ids[i], function() {});
            }
            $(t.target).addClass("m")
        }
        return void 0
    })
});