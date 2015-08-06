
from webhelpers2.html import escape, url_escape, literal

POST = 'post'
GET = 'get'


class htmltag(object):

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.class_ = escape(kwargs.get('class_', ''))
        self.container = None
        self.contents = []
        self.attrs = {}
        for (key, val) in kwargs.items():
            key = key.lower()
            if key in ['name', 'class_', 'id']:
                continue
            self.attrs[key] = val


    def add(self, *args):
        self.contents += args


    def attributes(self):
        attrs = []
        if self.name:
            attrs.append('name="%s" id="%s"' % (escape(self.name), escape(self.name)))
        if self.class_:
            attrs.append('class="%s"' % escape(self.class_))
        for (key, val) in self.attrs.items():
            attrs.append('%s="%s"' % (escape(key), escape(val)))
        return ' '.join(attrs)


    def __call__(self):
        return str(self)

    def __html__(self):
        return literal( str(self) )

    def __getitem__(self, arg):
        if type(arg) == tuple:
            self.add( * list(arg) )
        else:
            self.add( arg )
        return self


class form(htmltag):

    def __init__(self, name, action, method=GET, **kwargs):
        super().__init__( **kwargs )
        self.name = name
        self.action = action
        self.method = method


    def __str__(self):
        return literal( form_template.format( name=escape(self.name),
                                action = url_escape(self.action),
                                method = self.method,
                                contents = '\n'.join( escape(c) for c in self.contents ),
                        ) )


class input_text(htmltag):
    
    def __init__(self, name, label, value='', **kwargs):
        super().__init__( **kwargs )
        self.name = name
        self.label = label
        self.value = value

    def __str__(self):
        return literal( input_text_template.format( name=escape(self.name),
                        label=escape(self.label), value=escape(self.value),
                        class_div = 'form-group',
                        class_label = 'col-md-2 control-label',
                        class_value = 'col-md-10',
                        class_input = 'form-control',
                    ) )

class input_textarea(input_text):

    def __str__(self):
        return literal( input_textarea_template.format( name=escape(self.name),
                        label=escape(self.label), value=escape(self.value),
                        class_div = 'form-group',
                        class_label = 'col-md-2 control-label',
                        class_value = 'col-md-10',
                        class_input = 'form-control',
                    ) )

class input_hidden(htmltag):

    def __init__(self, name, value, **kwargs):
        super().__init__( **kwargs )
        self.name = name
        self.value = value

    def __str__(self):
        return literal( '<input type="hidden" id="%s" name="%s" value="%s" />' %
                        (escape(self.name), escape(self.name), escape(self.value)) )


class input_select(input_text):

    def __init__(self, name, label, value='', options=[], multiple=False, **kwargs):
        """ options: [ (val, label), ... ] """
        super().__init__( name, label, value, **kwargs )
        self.options = options
        self.multiple = multiple

    def __str__(self):
        options = []
        for val, label in self.options:
            selected = ''
            if self.value and self.value == key:
                selected = 'selected="selected"'
            options.append( '<option value="%s" %s>%s</option>' % 
                        (escape(val), selected, escape(label) ))
        return input_select_template.format(
                    name = escape(self.name), label = escape(self.label),
                    value = escape(self.value),
                    options = '\n'.join(options),
                    multiple = 'multiple="multiple"' if self.multiple else '',
                    class_div = 'form-group',
                    class_label = 'col-md-2 control-label',
                    class_value = 'col-md-10',
                    class_input = 'form-control',
                )

class input_select_ek(input_select):

    def __init__(self, name, label, value='', group=None, **kwargs):
        super().__init__( name, label, value, multiple=False, **kwargs )
        self.group = group
        dbh = get_dbhandler()
        self.options = None

    def __str__(self):
        return '<input>'


class doubletag(htmltag):
    
    _tag = ''

    def __init__(self, *args, **kwargs):
        super().__init__( **kwargs )
        self.contents = args

    def __str__(self):
        return literal( '<%s %s>%s</%s>' % ( self._tag, self.attributes(),
                                    '\n'.join( escape(str(c)) for c in self.contents ),
                                    self._tag )
                )

class image(htmltag):

    _tag = 'image'

    def __str__(self):
        return literal( '<%s %s />' % (self._tag, self.attributes()))

class p(doubletag):
    _tag = 'p'

class h1(doubletag):
    _tag = 'h1'

class h2(doubletag):
    _tag = 'h2'

class h3(doubletag):
    _tag = 'h3'

class span(doubletag):
    _tag = 'span'

class a(doubletag):
    _tag = 'a'

class div(doubletag):
    _tag = 'div'

    def __str__(self):
        return literal( '<%s %s>\n%s\n</%s>' % ( self._tag, self.attributes(),
                                        '\n'.join( escape(str(c)) for c in self.contents ),
                                        self._tag ) )

class ul(doubletag):
    _tag = 'ul'

    def __init__(self, *args, **kwargs):
        super().__init__( **kwargs )
        self.add_contents( *args )

    def add_contents(self, *args):
        for arg in args:
            if not isinstance(args, li):
                raise RuntimeError('UL should only have LI content')
            self.contents.append(arg)

class li(doubletag):
    _tag = 'li'


## tables

class table(doubletag):
    _tag = 'table'

class thead(doubletag):
    _tag = 'thead'

class tbody(doubletag):
    _tag = 'tbody'

class tr(doubletag):
    _tag = 'tr'

class th(doubletag):
    _tag = 'th'

class td(doubletag):
    _tag = 'td'

## singleton

BR = literal('<br/>')
HR = literal('<hr/>')


input_text_template = '''\
<div class='{class_div}'>
  <label class='{class_label}' for='{name}'>{label}</label>
  <div class='{class_value}'>
    <input type='text' id='{name}' name='{name}' value='{value}' class='{class_input}'/>
  </div>
</div>'''


input_hidden_template = '''\
<input type='hidden' id='{name}' name='{name}' value='{value}' />
'''

input_textarea_template = '''\
<div class='{class_div}'>
  <label class='{class_label}' for='{name}'>{label}</label>
  <div class='{class_value}'>
    <textarea id='{name}' name='{name}' class='{class_input}'>{value}</textarea>
  </div>
</div>'''

input_select_template = '''\
<div class='{class_div}'>
  <label class='{class_label}' for='{name}'>{label}</label>
  <div class='{class_value}'>
    <select id='{name}' name='{name}' class='{class_input}' {multiple}>
    {options}
    </select>
  </div>
</div>'''

radioboxes_template = '''\
<div class="{class_div}">
  <label class="{class_label}" for="{name}">{label}</label>
  % for (n, l, c) in params:
  <div class="controls">
    <label class="checkbox">
      <input id="${name}" type="checkbox" name="${n}" value="1" ${"checked='checked'" if c else ''} />
      ${l}
    </label>
  </div>
  % endfor
</div>'''

form_template = '''\
<form name="{name}" id="{name}" action="{action}" method="{method}" class="form-horizontal input-group-sm">
  {contents}
</form>'''
## test

