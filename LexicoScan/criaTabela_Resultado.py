import copy
import random
import unicodedata
import sys
import csv
import textwrap
import itertools

py3k = sys.version_info[0] >= 3
if py3k:
    unicode = str
    basestring = str
    itermap = map
    iterzip = zip
    uni_chr = chr
    from html.parser import HTMLParser
else: 
    itermap = itertools.imap
    iterzip = itertools.izip
    #uni_chr = unichr
    from HTMLParser import HTMLParser

if py3k and sys.version_info[1] >= 2:
    from html import escape
else:
    from cgi import escape

# estilos 
FRAME = 0
ALL   = 1
NONE  = 2
HEADER = 3

# Estilos de mesa
DEFAULT = 10
MSWORD_FRIENDLY = 11
PLAIN_COLUMNS = 12
RANDOM = 20

def _get_size(text):
    lines = text.split("\n")
    height = len(lines)
    width = max([_str_block_width(line) for line in lines])
    return (width, height)
        
class organizaTabela(object):

    def __init__(self, field_names=None, **kwargs):

        #Retorna uma nova instancia no metodo
        self.encoding = kwargs.get("encoding", "UTF-8")

        # Dados recebidos
        self._field_names = []
        self._align = {}
        self._valign = {}
        self._max_width = {}
        self._rows = []
        if field_names:
            self.field_names = field_names
        else:
            self._widths = []

        # Opçoes
        self._options = "start end fields header border sortby reversesort sort_key attributes format hrules vrules".split()
        self._options.extend("int_format float_format padding_width left_padding_width right_padding_width".split())
        self._options.extend("vertical_char horizontal_char junction_char header_style valign".split())
        for option in self._options:
            if option in kwargs:
                self._validate_option(option, kwargs[option])
            else:
                kwargs[option] = None

        self._start = kwargs["start"] or 0
        self._end = kwargs["end"] or None
        self._fields = kwargs["fields"] or None

        if kwargs["header"] in (True, False):
            self._header = kwargs["header"]
        else:
            self._header = True
        self._header_style = kwargs["header_style"] or None
        if kwargs["border"] in (True, False):
            self._border = kwargs["border"]
        else:
            self._border = True
        self._hrules = kwargs["hrules"] or FRAME
        self._vrules = kwargs["vrules"] or ALL

        self._sortby = kwargs["sortby"] or None
        if kwargs["reversesort"] in (True, False):
            self._reversesort = kwargs["reversesort"]
        else:
            self._reversesort = False
        self._sort_key = kwargs["sort_key"] or (lambda x: x)

        self._int_format = kwargs["int_format"] or {}
        self._float_format = kwargs["float_format"] or {}
        self._padding_width = kwargs["padding_width"] or 1
        self._left_padding_width = kwargs["left_padding_width"] or None
        self._right_padding_width = kwargs["right_padding_width"] or None

        self._vertical_char = kwargs["vertical_char"] or self._unicode("|")
        self._horizontal_char = kwargs["horizontal_char"] or self._unicode("-")
        self._junction_char = kwargs["junction_char"] or self._unicode("+")
        
        self._format = kwargs["format"] or False
        self._attributes = kwargs["attributes"] or {}
   
    def _unicode(self, value):
        if not isinstance(value, basestring):
            value = str(value)
        if not isinstance(value, unicode):
            value = unicode(value, self.encoding, "strict")
        return value

    def _justify(self, text, width, align):
        excess = width - _str_block_width(text)
        if align == "l":
            return text + excess * " "
        elif align == "r":
            return excess * " " + text
        else:
            if excess % 2:
                # Coloca mais espaço à direita se o texto tiver um comprimento diferente do esperado.
                if _str_block_width(text) % 2:
                    return (excess//2)*" " + text + (excess//2 + 1)*" "
                # Tambem mais espaço à esquerda se o texto for de comprimento uniforme.
                else:
                    return (excess//2 + 1)*" " + text + (excess//2)*" "
                # Por que distribuir espaço extra dessa forma? Para corresponder ao comportamento de o embutido str.center() method.
            else:
                # Preenchimento em ambos os lados.
                return (excess//2)*" " + text + (excess//2)*" "

    def __getattr__(self, name):

        if name == "rowcount":
            return len(self._rows)
        elif name == "colcount":
            if self._field_names:
                return len(self._field_names)
            elif self._rows:
                return len(self._rows[0])
            else:
                return 0
        else:
            raise AttributeError(name)
 
    def __getitem__(self, index):

        new = organizaTabela()
        new.field_names = self.field_names
        for attr in self._options:
            setattr(new, "_"+attr, getattr(self, "_"+attr))
        setattr(new, "_align", getattr(self, "_align"))
        if isinstance(index, slice):
            for row in self._rows[index]:
                new.add_row(row)
        elif isinstance(index, int):
            new.add_row(self._rows[index])
        else:
            raise Exception("Index %s is invalid, must be an integer or slice" % str(index))
        return new

    if py3k:
        def __str__(self):
           return self.__unicode__()
    else:
        def __str__(self):
           return self.__unicode__().encode(self.encoding)

    def __unicode__(self):
        return self.get_string()

	#VALIDADORES DE ATRIBUTOS

    def _validate_option(self, option, val):
        if option in ("field_names"):
            self._validate_field_names(val)
        elif option in ("start", "end", "max_width", "padding_width", "left_padding_width", "right_padding_width", "format"):
            self._validate_nonnegative_int(option, val)
        elif option in ("sortby"):
            self._validate_field_name(option, val)
        elif option in ("sort_key"):
            self._validate_function(option, val)
        elif option in ("hrules"):
            self._validate_hrules(option, val)
        elif option in ("vrules"):
            self._validate_vrules(option, val)
        elif option in ("fields"):
            self._validate_all_field_names(option, val)
        elif option in ("header", "border", "reversesort"):
            self._validate_true_or_false(option, val)
        elif option in ("header_style"):
            self._validate_header_style(val)
        elif option in ("int_format"):
            self._validate_int_format(option, val)
        elif option in ("float_format"):
            self._validate_float_format(option, val)
        elif option in ("vertical_char", "horizontal_char", "junction_char"):
            self._validate_single_char(option, val)
        elif option in ("attributes"):
            self._validate_attributes(option, val)
        else:
            raise Exception("Unrecognised option: %s!" % option)

    def _validate_field_names(self, val):
	
        # Verifica o comprimento apropriado
        if self._field_names:
            try:
               assert len(val) == len(self._field_names)
            except AssertionError:
               raise Exception("Field name list has incorrect number of values, (actual) %d!=%d (expected)" % (len(val), len(self._field_names)))
        if self._rows:
            try:
               assert len(val) == len(self._rows[0])
            except AssertionError:
               raise Exception("Field name list has incorrect number of values, (actual) %d!=%d (expected)" % (len(val), len(self._rows[0])))       
        try: # Verifique se há exclusividade
            assert len(val) == len(set(val))
        except AssertionError:
            raise Exception("Field names must be unique!")

    def _validate_header_style(self, val):
        try:
            assert val in ("cap", "title", "upper", "lower", None)
        except AssertionError:
            raise Exception("Invalid header style, use cap, title, upper, lower or None!")

    def _validate_align(self, val):
        try:
            assert val in ["l","c","r"]
        except AssertionError:
            raise Exception("Alignment %s is invalid, use l, c or r!" % val)

    def _validate_valign(self, val):
        try:
            assert val in ["t","m","b",None]
        except AssertionError:
            raise Exception("Alignment %s is invalid, use t, m, b or None!" % val)

    def _validate_nonnegative_int(self, name, val):
        try:
            assert int(val) >= 0
        except AssertionError:
            raise Exception("Invalid value for %s: %s!" % (name, self._unicode(val)))

    def _validate_true_or_false(self, name, val):
        try:
            assert val in (True, False)
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be True or False." % name)

    def _validate_int_format(self, name, val):
        if val == "":
            return
        try:
            assert type(val) in (str, unicode)
            assert val.isdigit()
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be an integer format string." % name)

    def _validate_float_format(self, name, val):
        if val == "":
            return
        try:
            assert type(val) in (str, unicode)
            assert "." in val
            bits = val.split(".")
            assert len(bits) <= 2
            assert bits[0] == "" or bits[0].isdigit()
            assert bits[1] == "" or bits[1].isdigit()
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be a float format string." % name)

    def _validate_function(self, name, val):
        try:
            assert hasattr(val, "__call__")
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be a function." % name)

    def _validate_hrules(self, name, val):
        try:
            assert val in (ALL, FRAME, HEADER, NONE)
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be ALL, FRAME, HEADER or NONE." % name)

    def _validate_vrules(self, name, val):
        try:
            assert val in (ALL, FRAME, NONE)
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be ALL, FRAME, or NONE." % name)

    def _validate_field_name(self, name, val):
        try:
            assert (val in self._field_names) or (val is None)
        except AssertionError:
            raise Exception("Invalid field name: %s!" % val)

    def _validate_all_field_names(self, name, val):
        try:
            for x in val:
                self._validate_field_name(name, x)
        except AssertionError:
            raise Exception("fields must be a sequence of field names!")

    def _validate_single_char(self, name, val):
        try:
            assert _str_block_width(val) == 1
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be a string of length 1." % name)

    def _validate_attributes(self, name, val):
        try:
            assert isinstance(val, dict)
        except AssertionError:
            raise Exception("attributes must be a dictionary of name/value pairs!")

    
    #GESTÃO DE ATRIBUTOS    
    def _get_field_names(self):
        return self._field_names
        
		#Os nomes dos campos      
    def _set_field_names(self, val):
        val = [self._unicode(x) for x in val]
        self._validate_option("field_names", val)
        if self._field_names:
            old_names = self._field_names[:]
        self._field_names = val
        if self._align and old_names:
            for old_name, new_name in zip(old_names, val):
                self._align[new_name] = self._align[old_name]
            for old_name in old_names:
                if old_name not in self._align:
                    self._align.pop(old_name)
        else:
            for field in self._field_names:
                self._align[field] = "c"
        if self._valign and old_names:
            for old_name, new_name in zip(old_names, val):
                self._valign[new_name] = self._valign[old_name]
            for old_name in old_names:
                if old_name not in self._valign:
                    self._valign.pop(old_name)
        else:
            for field in self._field_names:
                self._valign[field] = "t"
    field_names = property(_get_field_names, _set_field_names)

    def _get_align(self):
        return self._align
    def _set_align(self, val):
        self._validate_align(val)
        for field in self._field_names:
            self._align[field] = val
    align = property(_get_align, _set_align)

    def _get_valign(self):
        return self._valign
    def _set_valign(self, val):
        self._validate_valign(val)
        for field in self._field_names:
            self._valign[field] = val
    valign = property(_get_valign, _set_valign)

    def _get_max_width(self):
        return self._max_width
    def _set_max_width(self, val):
        self._validate_option("max_width", val)
        for field in self._field_names:
            self._max_width[field] = val
    max_width = property(_get_max_width, _set_max_width)
    
    def _get_fields(self):
        #Lista ou tupla de nomes de campo para incluir em exibições
        return self._fields
    def _set_fields(self, val):
        self._validate_option("fields", val)
        self._fields = val
    fields = property(_get_fields, _set_fields)

    def _get_start(self):
	
        #Índice inicial do intervalo de linhas a imprimir
        return self._start

    def _set_start(self, val):
        self._validate_option("start", val)
        self._start = val
    start = property(_get_start, _set_start)

    def _get_end(self):
        
		#Índice final do intervalo de linhas a imprimir
        return self._end
    def _set_end(self, val):
        self._validate_option("end", val)
        self._end = val
    end = property(_get_end, _set_end)

    def _get_sortby(self):
	
        #Name of field by which to sort rows
        return self._sortby
    def _set_sortby(self, val):
        self._validate_option("sortby", val)
        self._sortby = val
    sortby = property(_get_sortby, _set_sortby)

    def _get_reversesort(self):
	
        #Controla a direção da classificação "ascendente vs descendente"
        return self._reversesort
    def _set_reversesort(self, val):
        self._validate_option("reversesort", val)
        self._reversesort = val
    reversesort = property(_get_reversesort, _set_reversesort)

    def _get_sort_key(self):
	
        #Função chave de classificação, aplicada aos pontos de dados antes da classificação
        return self._sort_key
    def _set_sort_key(self, val):
        self._validate_option("sort_key", val)
        self._sort_key = val
    sort_key = property(_get_sort_key, _set_sort_key)
 
    def _get_header(self):
	
        #Controla a impressão do cabeçalho da tabela com os nomes dos campos
        return self._header
    def _set_header(self, val):
        self._validate_option("header", val)
        self._header = val
    header = property(_get_header, _set_header)

    def _get_header_style(self):
	
        #Controla a estilização aplicada a nomes de campo no cabeçalho
        return self._header_style
    def _set_header_style(self, val):
        self._validate_header_style(val)
        self._header_style = val
    header_style = property(_get_header_style, _set_header_style)

    def _get_border(self):
        
		#Controla a impressão da borda ao redor da mesa
        return self._border
    def _set_border(self, val):
        self._validate_option("border", val)
        self._border = val
    border = property(_get_border, _set_border)

    def _get_hrules(self):
	
        #Controla a impressão da borda ao redor da mesa
        return self._hrules
    def _set_hrules(self, val):
        self._validate_option("hrules", val)
        self._hrules = val
    hrules = property(_get_hrules, _set_hrules)

    def _get_vrules(self):
	
        #Controla a impressão de réguas verticais entre colunas
        return self._vrules
    def _set_vrules(self, val):
        self._validate_option("vrules", val)
        self._vrules = val
    vrules = property(_get_vrules, _set_vrules)

    def _get_int_format(self):
	
        #Controla a formatação de dados inteiros
        return self._int_format
    def _set_int_format(self, val):
        for field in self._field_names:
            self._int_format[field] = val
    int_format = property(_get_int_format, _set_int_format)

    def _get_float_format(self):
	
        #Controla a formatação de dados de ponto flutuante
        return self._float_format
    def _set_float_format(self, val):
        for field in self._field_names:
            self._float_format[field] = val
    float_format = property(_get_float_format, _set_float_format)

    def _get_padding_width(self):
	
        #O número de espaços vazios entre a borda de uma coluna e seu conteúdo
        return self._padding_width
    def _set_padding_width(self, val):
        self._validate_option("padding_width", val)
        self._padding_width = val
    padding_width = property(_get_padding_width, _set_padding_width)

    def _get_left_padding_width(self):
	
        #O número de espaços vazios entre a borda esquerda de uma coluna e seu conteúdo
        return self._left_padding_width
    def _set_left_padding_width(self, val):
        self._validate_option("left_padding_width", val)
        self._left_padding_width = val
    left_padding_width = property(_get_left_padding_width, _set_left_padding_width)

    def _get_right_padding_width(self):
	
        #O número de espaços vazios entre a borda direita de uma coluna e seu conteúdo
        return self._right_padding_width
    def _set_right_padding_width(self, val):
        self._validate_option("right_padding_width", val)
        self._right_padding_width = val
    right_padding_width = property(_get_right_padding_width, _set_right_padding_width)

    def _get_vertical_char(self):
	
        #O caractere usado ao imprimir as bordas da mesa para desenhar linhas verticais
        return self._vertical_char
    def _set_vertical_char(self, val):
        val = self._unicode(val)
        self._validate_option("vertical_char", val)
        self._vertical_char = val
    vertical_char = property(_get_vertical_char, _set_vertical_char)

    def _get_horizontal_char(self):
	
        #O caractere usado ao imprimir as bordas da mesa para desenhar linhas horizontais
        return self._horizontal_char
    def _set_horizontal_char(self, val):
        val = self._unicode(val)
        self._validate_option("horizontal_char", val)
        self._horizontal_char = val
    horizontal_char = property(_get_horizontal_char, _set_horizontal_char)

    def _get_junction_char(self):
	
        #O caractere usado ao imprimir bordas de mesa para desenhar junções de linha
        return self._junction_char
    def _set_junction_char(self, val):
        val = self._unicode(val)
        self._validate_option("vertical_char", val)
        self._junction_char = val
    junction_char = property(_get_junction_char, _set_junction_char)

    def _get_format(self):
	
        #Controla se as tabelas HTML são formatadas ou não para corresponder às opções de estilo
        return self._format
    def _set_format(self, val):
        self._validate_option("format", val)
        self._format = val
    format = property(_get_format, _set_format)

    def _get_attributes(self):
	
        #Um dicionário de pares de nome / valor de atributo HTML a ser incluído na 
		#tag <table> ao imprimir HTML
        return self._attributes
    def _set_attributes(self, val):
        self._validate_option("attributes", val)
        self._attributes = val
    attributes = property(_get_attributes, _set_attributes)

    # COMBINADOR DE OPCOES      
    def _get_options(self, kwargs):

        options = {}
        for option in self._options:
            if option in kwargs:
                self._validate_option(option, kwargs[option])
                options[option] = kwargs[option]
            else:
                options[option] = getattr(self, "_"+option)
        return options

    # LÓGICA DE ESTILO PREDEFINIDO       
    def set_style(self, style):

        if style == DEFAULT:
            self._set_default_style()
        elif style == MSWORD_FRIENDLY:
            self._set_msword_style()
        elif style == PLAIN_COLUMNS:
            self._set_columns_style()
        elif style == RANDOM:
            self._set_random_style()
        else:
            raise Exception("Invalid pre-set style!")

    def _set_default_style(self):

        self.header = True
        self.border = True
        self._hrules = FRAME
        self._vrules = ALL
        self.padding_width = 1
        self.left_padding_width = 1
        self.right_padding_width = 1
        self.vertical_char = "|"
        self.horizontal_char = "-"
        self.junction_char = "+"

    def _set_msword_style(self):

        self.header = True
        self.border = True
        self._hrules = NONE
        self.padding_width = 1
        self.left_padding_width = 1
        self.right_padding_width = 1
        self.vertical_char = "|"

    def _set_columns_style(self):

        self.header = True
        self.border = False
        self.padding_width = 1
        self.left_padding_width = 0
        self.right_padding_width = 8

    def _set_random_style(self):

        # Just for fun!
        self.header = random.choice((True, False))
        self.border = random.choice((True, False))
        self._hrules = random.choice((ALL, FRAME, HEADER, NONE))
        self._vrules = random.choice((ALL, FRAME, NONE))
        self.left_padding_width = random.randint(0,5)
        self.right_padding_width = random.randint(0,5)
        self.vertical_char = random.choice("~!@#$%^&*()_+|-=\{}[];':\",./;<>?")
        self.horizontal_char = random.choice("~!@#$%^&*()_+|-=\{}[];':\",./;<>?")
        self.junction_char = random.choice("~!@#$%^&*()_+|-=\{}[];':\",./;<>?")


    # MÉTODOS DE ENTRADA DE DADOS         

    def add_row(self, row):

        #Adicione uma linha à tabela
        if self._field_names and len(row) != len(self._field_names):
            raise Exception("Row has incorrect number of values, (actual) %d!=%d (expected)" %(len(row),len(self._field_names)))
        if not self._field_names:
            self.field_names = [("Field %d" % (n+1)) for n in range(0,len(row))]
        self._rows.append(list(row))

    def del_row(self, row_index):

        #Exclua uma linha da tabela
        if row_index > len(self._rows)-1:
            raise Exception("Cant delete row at index %d, table only has %d rows!" % (row_index, len(self._rows)))
        del self._rows[row_index]

    def add_column(self, fieldname, column, align="c", valign="t"):

        #Adicione uma coluna à tabela.
        if len(self._rows) in (0, len(column)):
            self._validate_align(align)
            self._validate_valign(valign)
            self._field_names.append(fieldname)
            self._align[fieldname] = align
            self._valign[fieldname] = valign
            for i in range(0, len(column)):
                if len(self._rows) < i+1:
                    self._rows.append([])
                self._rows[i].append(column[i])
        else:
            raise Exception("Column length %d does not match number of rows %d!" % (len(column), len(self._rows)))

    def clear_rows(self):

        #Exclua todas as linhas da tabela, mas mantenha os nomes dos campos atuais
        self._rows = []

    def clear(self):

        #Exclua todas as linhas e nomes de campo da tabela, mantendo nada além de opções de estilo
        self._rows = []
        self._field_names = []
        self._widths = []


    # MÉTODOS PÚBLICOS        
    def copy(self):
        return copy.deepcopy(self)

    # MÉTODOS PRIVADOS      
    def _format_value(self, field, value):
        if isinstance(value, int) and field in self._int_format:
            value = self._unicode(("%%%sd" % self._int_format[field]) % value)
        elif isinstance(value, float) and field in self._float_format:
            value = self._unicode(("%%%sf" % self._float_format[field]) % value)
        return self._unicode(value)

    def _compute_widths(self, rows, options):
        if options["header"]:
            widths = [_get_size(field)[0] for field in self._field_names]
        else:
            widths = len(self.field_names) * [0]
        for row in rows:
            for index, value in enumerate(row):
                fieldname = self.field_names[index]
                if fieldname in self.max_width:
                    widths[index] = max(widths[index], min(_get_size(value)[0], self.max_width[fieldname]))
                else:
                    widths[index] = max(widths[index], _get_size(value)[0])
        self._widths = widths

    def _get_padding_widths(self, options):

        if options["left_padding_width"] is not None:
            lpad = options["left_padding_width"]
        else:
            lpad = options["padding_width"]
        if options["right_padding_width"] is not None:
            rpad = options["right_padding_width"]
        else:
            rpad = options["padding_width"]
        return lpad, rpad

    def _get_rows(self, options):
	
        #Retorne apenas as linhas de dados que devem ser impressas, com base na divisão e classificação.
       
        # Faça uma cópia apenas dessas linhas no intervalo da fatia 
        rows = copy.deepcopy(self._rows[options["start"]:options["end"]])
		
        # Classifique se necessário
        if options["sortby"]:
            sortindex = self._field_names.index(options["sortby"])
            rows = [[row[sortindex]]+row for row in rows]
            # Ordenar
            rows.sort(reverse=options["reversesort"], key=options["sort_key"])
            rows = [row[1:] for row in rows]
        return rows
        
    def _format_row(self, row, options):
        return [self._format_value(field, value) for (field, value) in zip(self._field_names, row)]

    def _format_rows(self, rows, options):
        return [self._format_row(row, options) for row in rows]
 

    # MÉTODOS DE CADEIA DE TEXTO SIMPLES  
    def get_string(self, **kwargs):

        #Return string representation of table in current state.
        options = self._get_options(kwargs)

        lines = []

        if self.rowcount == 0:
            return ""

        # Obtenha as linhas que precisamos imprimir, levando em 
		# consideração o corte, a classificação, etc...
        rows = self._get_rows(options)

        # Transforme todos os dados em todas as linhas em Unicode, formatado conforme desejado
        formatted_rows = self._format_rows(rows, options)

        # Calcular larguras de coluna
        self._compute_widths(formatted_rows, options)

        # Adicionar cabeçalho ou topo da borda
        self._hrule = self._stringify_hrule(options)
        if options["header"]:
            lines.append(self._stringify_header(options))
        elif options["border"] and options["hrules"] in (ALL, FRAME):
            lines.append(self._hrule)

        # Adicionar linhas
        for row in formatted_rows:
            lines.append(self._stringify_row(row, options))

        # Adicionar parte inferior da borda
        if options["border"] and options["hrules"] == FRAME:
            lines.append(self._hrule)
        
        return self._unicode("\n").join(lines)

    def _stringify_hrule(self, options):

        if not options["border"]:
            return ""
        lpad, rpad = self._get_padding_widths(options)
        bits = [options["junction_char"]]
        for field, width in zip(self._field_names, self._widths):
            if options["fields"] and field not in options["fields"]:
                continue
            bits.append((width+lpad+rpad)*options["horizontal_char"])
            bits.append(options["junction_char"])
        return "".join(bits)

    def _stringify_header(self, options):

        bits = []
        lpad, rpad = self._get_padding_widths(options)
        if options["border"]:
            if options["hrules"] in (ALL, FRAME):
                bits.append(self._hrule)
                bits.append("\n")
            if options["vrules"] in (ALL, FRAME):
                bits.append(options["vertical_char"])
            else:
                bits.append(" ")
        for field, width, in zip(self._field_names, self._widths):
            if options["fields"] and field not in options["fields"]:
                continue
            if self._header_style == "cap":
                fieldname = field.capitalize()
            elif self._header_style == "title":
                fieldname = field.title()
            elif self._header_style == "upper":
                fieldname = field.upper()
            elif self._header_style == "lower":
                fieldname = field.lower()
            else:
                fieldname = field
            bits.append(" " * lpad + self._justify(fieldname, width, self._align[field]) + " " * rpad)
            if options["border"]:
                if options["vrules"] == ALL:
                    bits.append(options["vertical_char"])
                else:
                    bits.append(" ")
					
        # Se vrules for FRAME, então apenas acrescentamos um espaço no final
        # do último campo, quando realmente queremos um caractere vertical
        if options["border"] and options["vrules"] == FRAME:
            bits.pop()
            bits.append(options["vertical_char"])
        if options["border"] and options["hrules"] != NONE:
            bits.append("\n")
            bits.append(self._hrule)
        return "".join(bits)

    def _stringify_row(self, row, options):
       
        for index, field, value, width, in zip(range(0,len(row)), self._field_names, row, self._widths):
            # Aplicar larguras máximas
            lines = value.split("\n")
            new_lines = []
            for line in lines: 
                if _str_block_width(line) > width:
                    line = textwrap.fill(line, width)
                new_lines.append(line)
            lines = new_lines
            value = "\n".join(lines)
            row[index] = value

        row_height = 0
        for c in row:
            h = _get_size(c)[1]
            if h > row_height:
                row_height = h

        bits = []
        lpad, rpad = self._get_padding_widths(options)
        for y in range(0, row_height):
            bits.append([])
            if options["border"]:
                if options["vrules"] in (ALL, FRAME):
                    bits[y].append(self.vertical_char)
                else:
                    bits[y].append(" ")

        for field, value, width, in zip(self._field_names, row, self._widths):

            valign = self._valign[field]
            lines = value.split("\n")
            dHeight = row_height - len(lines)
            if dHeight:
                if valign == "m":
                  lines = [""] * int(dHeight / 2) + lines + [""] * (dHeight - int(dHeight / 2))
                elif valign == "b":
                  lines = [""] * dHeight + lines
                else:
                  lines = lines + [""] * dHeight

            y = 0
            for l in lines:
                if options["fields"] and field not in options["fields"]:
                    continue

                bits[y].append(" " * lpad + self._justify(l, width, self._align[field]) + " " * rpad)
                if options["border"]:
                    if options["vrules"] == ALL:
                        bits[y].append(self.vertical_char)
                    else:
                        bits[y].append(" ")
                y += 1

        # Se vrules for FRAME, então apenas acrescentamos um espaço no final
        # do último campo, quando realmente queremos um caractere vertical
        for y in range(0, row_height):
            if options["border"] and options["vrules"] == FRAME:
                bits[y].pop()
                bits[y].append(options["vertical_char"])
        
        if options["border"] and options["hrules"]== ALL:
            bits[row_height-1].append("\n")
            bits[row_height-1].append(self._hrule)

        for y in range(0, row_height):
            bits[y] = "".join(bits[y])

        return "\n".join(bits)

    # HTML CADEIA METODOS  

    def get_html_string(self, **kwargs):

        #Retorne a representação de string da versão formatada em HTML da tabela no estado atual.

        options = self._get_options(kwargs)

        if options["format"]:
            string = self._get_formatted_html_string(options)
        else:
            string = self._get_simple_html_string(options)

        return string

    def _get_simple_html_string(self, options):

        lines = []

        open_tag = []
        open_tag.append("<table")
        if options["attributes"]:
            for attr_name in options["attributes"]:
                open_tag.append(" %s=\"%s\"" % (attr_name, options["attributes"][attr_name]))
        open_tag.append(">")
        lines.append("".join(open_tag))

        # Cabeçalhos
        if options["header"]:
            lines.append("    <tr>")
            for field in self._field_names:
                if options["fields"] and field not in options["fields"]:
                    continue
                lines.append("        <th>%s</th>" % escape(field).replace("\n", "<br />"))
            lines.append("    </tr>")

        # DADOS
        rows = self._get_rows(options)
        formatted_rows = self._format_rows(rows, options)
        for row in formatted_rows:
            lines.append("    <tr>")
            for field, datum in zip(self._field_names, row):
                if options["fields"] and field not in options["fields"]:
                    continue
                lines.append("        <td>%s</td>" % escape(datum).replace("\n", "<br />"))
            lines.append("    </tr>")

        lines.append("</table>")

        return self._unicode("\n").join(lines)

    def _get_formatted_html_string(self, options):

        lines = []
        lpad, rpad = self._get_padding_widths(options)

        open_tag = []
        open_tag.append("<table")
        if options["border"]:
            if options["hrules"] == ALL and options["vrules"] == ALL:
                open_tag.append(" frame=\"box\" rules=\"all\"")
            elif options["hrules"] == FRAME and options["vrules"] == FRAME:
                open_tag.append(" frame=\"box\"")
            elif options["hrules"] == FRAME and options["vrules"] == ALL:
                open_tag.append(" frame=\"box\" rules=\"cols\"")
            elif options["hrules"] == FRAME:
                open_tag.append(" frame=\"hsides\"")
            elif options["hrules"] == ALL:
                open_tag.append(" frame=\"hsides\" rules=\"rows\"")
            elif options["vrules"] == FRAME:
                open_tag.append(" frame=\"vsides\"")
            elif options["vrules"] == ALL:
                open_tag.append(" frame=\"vsides\" rules=\"cols\"")
        if options["attributes"]:
            for attr_name in options["attributes"]:
                open_tag.append(" %s=\"%s\"" % (attr_name, options["attributes"][attr_name]))
        open_tag.append(">")
        lines.append("".join(open_tag))

        # Cabeçalhos
        if options["header"]:
            lines.append("    <tr>")
            for field in self._field_names:
                if options["fields"] and field not in options["fields"]:
                    continue
                lines.append("        <th style=\"padding-left: %dem; padding-right: %dem; text-align: center\">%s</th>" % (lpad, rpad, escape(field).replace("\n", "<br />")))
            lines.append("    </tr>")

        # Dados
        rows = self._get_rows(options)
        formatted_rows = self._format_rows(rows, options)
        aligns = []
        valigns = []
        for field in self._field_names:
            aligns.append({ "l" : "left", "r" : "right", "c" : "center" }[self._align[field]])
            valigns.append({"t" : "top", "m" : "middle", "b" : "bottom"}[self._valign[field]])
        for row in formatted_rows:
            lines.append("    <tr>")
            for field, datum, align, valign in zip(self._field_names, row, aligns, valigns):
                if options["fields"] and field not in options["fields"]:
                    continue
                lines.append("        <td style=\"padding-left: %dem; padding-right: %dem; text-align: %s; vertical-align: %s\">%s</td>" % (lpad, rpad, align, valign, escape(datum).replace("\n", "<br />")))
            lines.append("    </tr>")
        lines.append("</table>")

        return self._unicode("\n").join(lines)

# FUNÇÕES DE LARGURA UNICODE   

def _char_block_width(char):
    # Latim básico, que provavelmente é o cas mais comum, se char em xrange(0x0021, 0x007e):
    #se char >= 0x0021 e char <= 0x007e:
    if 0x0021 <= char <= 0x007e:
        return 1     
    if 0x4e00 <= char <= 0x9fff:     			 	 # Japanese, Korean, Chinese
        return 2
    if 0xac00 <= char <= 0xd7af:      				 # Hangul
        return 2
    if unicodedata.combining(uni_chr(char)):     	 # Combining?
        return 0
    if 0x3040 <= char <= 0x309f or 0x30a0 <= char <= 0x30ff:  # Hiragana and Katakana
        return 2
    if 0xff01 <= char <= 0xff60:     				# Full-width Latin characters
        return 2
    if 0x3000 <= char <= 0x303e:     				# CJK punctuation
        return 2
    if char in (0x0008, 0x007f):      				# Backspace and delete
        return -1
    elif char in (0x0000, 0x001f):   			    # Other control characters
        return 0
    return 1

def _str_block_width(val):

    return sum(itermap(_char_block_width, itermap(ord, val)))

# TABLE de FATORES            

def from_csv(fp, field_names = None, **kwargs):

    dialect = csv.Sniffer().sniff(fp.read(1024))
    fp.seek(0)
    reader = csv.reader(fp, dialect)

    table = organizaTabela(**kwargs)
    if field_names:
        table.field_names = field_names
    else:
        if py3k:
            table.field_names = [x.strip() for x in next(reader)]
        else:
            table.field_names = [x.strip() for x in reader.next()]

    for row in reader:
        table.add_row([x.strip() for x in row])

    return table

def from_db_cursor(cursor, **kwargs):

    if cursor.description:
        table = organizaTabela(**kwargs)
        table.field_names = [col[0] for col in cursor.description]
        for row in cursor.fetchall():
            table.add_row(row)
        return table

class TableHandler(HTMLParser):

    def __init__(self, **kwargs):
        HTMLParser.__init__(self)
        self.kwargs = kwargs
        self.tables = []
        self.last_row = []
        self.rows = []
        self.max_row_width = 0
        self.active = None
        self.last_content = ""
        self.is_last_row_header = False

    def handle_starttag(self,tag, attrs):
        self.active = tag
        if tag == "th":
            self.is_last_row_header = True

    def handle_endtag(self,tag):
        if tag in ["th", "td"]:
            stripped_content = self.last_content.strip()
            self.last_row.append(stripped_content)
        if tag == "tr":
            self.rows.append(
                (self.last_row, self.is_last_row_header))
            self.max_row_width = max(self.max_row_width, len(self.last_row))
            self.last_row = []
            self.is_last_row_header = False
        if tag == "table":
            table = self.generate_table(self.rows)
            self.tables.append(table)
            self.rows = []
        self.last_content = " "
        self.active = None


    def handle_data(self, data):
        self.last_content += data

    def generate_table(self, rows):

        #Gera de uma lista de linhas um objeto PrettyTable.
        table = organizaTabela(**self.kwargs)
        for row in self.rows:
            if len(row[0]) < self.max_row_width:
                appends = self.max_row_width - len(row[0])
                for i in range(1,appends):
                    row[0].append("-")

            if row[1] == True:
                self.make_fields_unique(row[0])
                table.field_names = row[0]
            else:
                table.add_row(row[0])
        return table

    def make_fields_unique(self, fields):
        
        #itera sobre a linha e torna cada campo único
        for i in range(0, len(fields)):
            for j in range(i+1, len(fields)):
                if fields[i] == fields[j]:
                    fields[j] += "'"

def from_html(html_code, **kwargs):

    #Gera uma lista de PrettyTables a partir de uma string de código HTML. 
    #Cada <table> em HTML torna-se um objeto PrettyTable.

    parser = TableHandler(**kwargs)
    parser.feed(html_code)
    return parser.tables

def from_html_one(html_code, **kwargs):

    #Gera PrettyTables a partir de uma string de código HTML que contém apenas uma única <table>
    tables = from_html(html_code, **kwargs)
    try:
        assert len(tables) == 1
    except AssertionError:
        raise Exception("More than one <table> in provided HTML code!  Use from_html instead.")
    return tables[0]

# MAIN "FUNÇÃO DE TESTE"    

def main():

    x = organizaTabela(["City name", "Area", "Population", "Annual Rainfall"])
    x.sortby = "Population"
    x.reversesort = True
    x.int_format["Area"] = "04d"
    x.float_format = "6.1f"
	# Alinhar nomes de cidades à esquerda
    x.align["City name"] = "l" 
    x.add_row(["Adelaide", 1295, 1158259, 600.5])
    x.add_row(["Brisbane", 5905, 1857594, 1146.4])
    x.add_row(["Darwin", 112, 120900, 1714.7])
    x.add_row(["Hobart", 1357, 205556, 619.5])
    x.add_row(["Sydney", 2058, 4336374, 1214.8])
    x.add_row(["Melbourne", 1566, 3806092, 646.9])
    x.add_row(["Perth", 5386, 1554769, 869.4])
    print(x)
    
if __name__ == "__main__":
    main()
