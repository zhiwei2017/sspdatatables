{% load static %}

{% load form_field %}

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
function button_search(table_obj, filter_container_id, trigger_btn_container_id, trigger_btns) {
    var that = table_obj;

    var trigger_btn_container = table_obj.table().container();
    if (trigger_btn_container_id != null)
        trigger_btn_container = "#"+trigger_btn_container_id;

    var filter_obj_array = table_obj.table().container().id;
    if (filter_container_id != null)
        filter_obj_array = filter_container_id;
    filter_obj_array = "#"+filter_obj_array+" input, #"+filter_obj_array+" select";
    filter_obj_array = $(filter_obj_array);

    $(trigger_btn_container).on('click', trigger_btns, function(e) {
        var erase_triggered = /_filter_erase_btn/g.test($(this).prop('id'));
        $.each(filter_obj_array, function(index, item) {
            var col_num= $(item).prop('id').match(/\d+/g);
            if (col_num == null)
                return;
            if (erase_triggered) {
                $(item).val("");
            }
            that = that.columns(col_num).search($(item).val());
        });
        // apply the filters
        that.draw();
    });
}

// direct search, which was triggered when the user input something or select
// something
function direct_search(table_obj, filter_container_id) {
    var that = table_obj;

    var filter_container_obj = table_obj.table().container();
    if (filter_container_id != null)
        filter_container_obj = $("#"+filter_container_id);

    $(filter_container_obj).on('keypress', 'input', function(e) {
        if (e.which == 13) {
            e.preventDefault();
            var col_num= $(this).attr('id').match(/\d+/g);
            if (col_num == null)
                return;
            that.columns( col_num )
                .search( this.value )
                .draw();
        }
    });
    $(filter_container_obj).on('change', 'select', function(e) {
        e.preventDefault();
        var col_num= $(this).attr('id').match(/\d+/g);
        if (col_num == null)
                return;
        var search_val = $(this).val();
        that.columns( col_num )
            .search( search_val )
            .draw();
    });
}

// apply the search according to the inputs in the filters
// the search can be trigger either by button click or by pressing return key
// for input field and changing value for drop-down
function apply_search(table_obj, filter_container_id=null, trigger_btn_container_id=null) {
    // if the trigger buttons exist, then use the button search function
    var table_id = table_obj.table().node().id;
    var trigger_btns = "#" + table_id+"_filter_erase_btn, #"+table_id+"_filter_search_btn";
    if ($(trigger_btns).length)
        return button_search(table_obj, filter_container_id, trigger_btn_container_id, trigger_btns);
    // if no trigger button, then use default search function
    return direct_search(table_obj, filter_container_id);
}

$(document).ready(function() {
    {% for item in sspdtable.frame %}
        {% with index=forloop.counter0 %}
            {% if item.searchable %}
                {% if item.filter_type == 'input' %}
                    var content = '<input id="' + "{{sspdtable.id}}" + '_column_' + '{{index}}';
                    content += '_search" type="text" class="form-control" placeholder="';
                    {% if item.placeholder %}
                        content += "{{item.placeholder}}";
                    {% else %}
                        content += "{{item.header}}";
                    {% endif %};
                    content += '" />';
                {% else %}
                    var content = '<{{item.filter_type}} id="';
                    content += "{{sspdtable.id}}" + '_column_' + '{{index}}';
                    content += '_search" class="form-control" name="';
                    content += "{{item.header}}".toLowerCase()  + '" >';
                    {% with field=sspdtable.footer_form|get_form_bound_field:item.id %}
                        {% for choice in field %}
                            content += '{{choice}}'
                        {% endfor %}
                    {% endwith %}
                    content += '</{{item.filter_type}}>';
                {% endif %}
                $("#"+"{{sspdtable.id}}_filter_{{item.id}}").html(content);
            {% endif %}
        {% endwith %}
    {% endfor %}
});
</script>