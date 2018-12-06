{% load static %}

{# this css can be disabled #}
{% if not auto_width %}
    <style>
        .form-control {
            width: 100% !important;
        }
    </style>
{% endif %}

{% block additionalScript %}
{% endblock %}

<script type="text/javascript" charset="utf-8">
// used for capitalize a string
String.prototype.capitalize = function() {
    return this.replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
};

// apply the search in the footers
// for the normal input footer, the user must hit the return key to trigger the search
function apply_search(js_object) {
    var that = js_object;

    $(js_object.table().container()).on('keypress', 'tfoot input', function(e) {
        if (e.which == 13) {
            e.preventDefault();
            var col_num= $(this).attr('id').match(/\d+/g);
            that.columns( col_num )
                .search( this.value )
                .draw();
        }
    });
    $(js_object.table().container()).on('change', 'tfoot select', function(e) {
        e.preventDefault();
        var col_num= $(this).attr('id').match(/\d+/g);
        var search_val = $(this).val();
        that.columns( col_num )
            .search( search_val )
            .draw();
    });
}
</script>