{% load static %}
<!-- DataTables CSS -->
<link href="https://cdn.datatables.net/1.10.19/css/dataTables.bootstrap.min.css" rel="stylesheet"/>
<link href="https://cdn.datatables.net/1.10.19/css/dataTables.bootstrap4.min.css" rel="stylesheet"/>

<!-- DataTables Responsive CSS -->
<link href="https://cdn.datatables.net/responsive/2.2.3/css/responsive.bootstrap.min.css" rel="stylesheet"/>
<link href="https://cdn.datatables.net/responsive/2.2.3/css/responsive.bootstrap4.min.css" rel="stylesheet"/>

<!-- DataTables JavaScript -->
<script type="text/javascript" src="https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.19/js/dataTables.bootstrap.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.19/js/dataTables.bootstrap4.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/responsive/2.2.3/js/dataTables.responsive.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/responsive/2.2.3/js/responsive.bootstrap.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/responsive/2.2.3/js/responsive.bootstrap4.min.js"></script>

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