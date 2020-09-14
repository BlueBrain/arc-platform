from django import forms


class ArcSelect(forms.Select):
    addValue = True

    def __init__(self, attrs=None, choices=(), addValue=True):
        super().__init__(attrs=attrs, choices=choices)
        self.addValue = addValue

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        if self.addValue:
            widget = context['widget']
            attrs = widget['attrs']

            # TODO this is currently not working with multi selects
            if 'value' not in attrs.keys() and 'value' in widget.keys():
                value = widget['value']
                if len(value) == 1:
                    attrs['value'] = value[0]

        return context

    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs=attrs, renderer=renderer)

        html = html \
            .replace("<select ", "<arc-select ") \
            .replace("</select>", "</arc-select>")

        return html
