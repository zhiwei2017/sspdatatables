{% load form_field %}

<script type="text/javascript" charset="utf-8">
$(document).ready(function() {
    {% for item in sspdtable.frame %}
        {% with index=forloop.counter0 %}
            {% if item.searchable %}
                {% if item.footer_type == 'input' %}
                    var content = '<input id="' + "{{sspdtable.id}}" + '_column_' + '{{index}}';
                    content += '_search" type="text" class="form-control" placeholder="';
                    {% if item.placeholder %}
                        content += "{{item.placeholder}}";
                    {% else %}
                        content += "{{item.header}}";
                    {% endif %};
                    content += '" />';
                {% else %}
                    var content = '<{{item.footer_type}} id="';
                    content += "{{sspdtable.id}}" + '_column_' + '{{index}}';
                    content += '_search" class="form-control" name="';
                    content += "{{item.header}}".toLowerCase()  + '" >';
                    {% with field=sspdtable.footer_form|get_form_bound_field:item.id %}
                        {% for choice in field %}
                            content += '{{choice}}'
                        {% endfor %}
                    {% endwith %}
                    content += '</{{item.footer_type}}>';
                {% endif %}
                $("#"+"{{sspdtable.id}}_{{item.id}}").html(content);
            {% endif %}
        {% endwith %}
    {% endfor %}
});
</script>