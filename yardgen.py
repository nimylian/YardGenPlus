import sublime, sublime_plugin
import re, time, os

class YardGenCommand(sublime_plugin.TextCommand):

  def load_config(self):
    self.settings = {}
    settings = sublime.load_settings('yardgen.sublime-settings')
    for setting in ['author', 'initial_empty_line']:
      if settings.get(setting) is None:
        continue
      self.settings[setting] = settings.get(setting)

  def current_position(self):
    return self.view.sel()[0].end()

  # Return the start and end position of the line(s)
  # where the selection is on
  def region_for_selection(self,selection):
    return self.view.line(selection)

  # Return the line(s) for where the current selection
  # is on.
  def line_for_selection(self,selection):
    region = self.region_for_selection(selection)
    return self.view.substr(region)

  # Return the scope
  def ruby_scope(self):
    scope = self.view.scope_name(self.current_position())
    if not re.search("source\\.ruby", scope):
      return False
    return True

  def line_ending(self):
    ending = "\n"
    if(self.view.line_endings() == "Windows"):
        ending = "\r\n"
    return ending

  def run_command(self, edit, str):
    if None == str:
        return
    self.cursor_to_the_left()
    self.view.insert(edit,self.view.sel()[0].begin(),"\n")
    self.cursor_to_the_left(-1)
    self.view.run_command(
        'insert_snippet', {
            'contents': str.decode('utf-8') if hasattr(str, 'decode') else bytes(str, 'utf-8').decode('utf-8')
        }
    )

  def region_for_line_after_selection(self,selection):
    region = self.region_for_selection(selection)
    selection = sublime.Region(region.end()+1, region.end()+1)
    region = self.region_for_selection(selection)
    return region

  def print_region(self,region):
    if self.debug_body_parser:
      print("---   Region   ---")
      print(region)
      print("'%s'" % (self.view.substr(region)))
      print("--- end region ---")

  def full_method_body(self,selection):
    maximum = self.view.size()
    region = self.region_for_selection(selection)
    if self.debug_body_parser:
      print(maximum)

    # We need to keep track off the block.
    # We are seeking the end that closes the method.
    # We recognize the following cases:
    #   do - unconditionally
    #   if - When at the start of the line
    # For every do we find we increment the depth counter
    # If the depth counter reaches zero we are there
    depth_counter = 1
    counter = 0
    region_start = region.begin()
    if self.debug_body_parser:
      print("Region_start = " + str(region_start))
    while True:
      if region.begin() >= maximum:
        if self.debug_body_parser:
          print("Break on maximum")
        break
      region = self.region_for_line_after_selection(region)
      line = self.view.substr(region)
      if re.search("\Wdo\W",line):
        if self.debug_body_parser:
          print("Increasing depth counter for [do] to [%d] on: '%s'" % (depth_counter,line))
        depth_counter += 1
      if re.search("^\s*if\W",line):
        if self.debug_body_parser:
          print("Increasing depth counter for [if] to [%d] on: '%s'" % (depth_counter,line))
        depth_counter += 1
      if re.search("^\s*case\W|\Wcase\W",line):
        if self.debug_body_parser:
          print("Increasing depth counter for [case] to [%d] on: '%s'" % (depth_counter,line))
        depth_counter += 1
      if re.search("\Wend\W|^\s*end\s*$",line):
        if self.debug_body_parser:
          print("Decreasing depth counter for [end] to [%d] on: '%s'" % (depth_counter,line))
        depth_counter -= 1
      if depth_counter == 0:
        if self.debug_body_parser:
          print("Break on depth counter reaching zero")
        break
      counter += 1
      # FJR - Keep this in as a precaution. SHOULD normally not happy
      if counter == 2000:
        print("****** Break on counter 2000")
        break

    # Done. Move to the next line. The cursor is now at the line with end
    region = self.region_for_line_after_selection(region)
    region_end = region.begin()
    if self.debug_body_parser:
      print("region_end = " + str(region_end))

    return_region = sublime.Region(region_start,region_end)
    self.print_region(return_region)
    return return_region

  # The plugin main entry
  def run(self,edit):
    self.debug_method = False
    self.debug_body_parser = False
    self.load_config()
    self.yield_regex = re.compile("""
      \Wyield
      (?:     # Different possibilities to find the arguments
        \s*   # Optional white space
        \(    # Opening parenthesis
      |
        \s+   # Just white space
      )
      (?P<args>  # The arguments
        [^)}\n\s]+
      )?
      """, re.X)
    cp = self.current_position()
    # Only do this for ruby scope
    if not self.ruby_scope():
      return
    # Loop over the various selections. In theory there could be multiple
    # selections.
    self.count = 1
    for selection in reversed(self.view.sel()):      # Get the current line where the cursor is
      line_for_selection = self.line_for_selection(selection)
      # Is it a method?
      r = re.search("(?P<indent>^\s*)def\s+(?P<name>.*?)(\((?P<args>.*)\))?$",line_for_selection)
      if not r == None:
        self.handle_method(edit,selection,r)
      # Is it a constant?
      r = re.search("(?P<indent>^\s*)(?P<constant>[A-Z][A-Z0-9_]*)\s*=\s*.*$",line_for_selection)
      if not r == None:
        self.handle_constant(edit,r)
      # Is it a module?
      r = re.search("(?P<indent>^\s*)(?P<mod_or_class>module|class)\s+(?P<name>[A-Z][a-zA-Z0-9]*(::[A-Z][a-zA-Z0-9]*)*).*?$",line_for_selection)
      if not r == None:
        self.handle_module(edit,r)
      # Is it a attr_reader, attr_writer or attr_accessor?
      r = re.search("(?P<indent>^\s*)(?P<attribute>attr_reader|attr_writer|attr_accessor)\s+:(?P<name>[a-z][a-zA-Z0-9_]*).*?$",line_for_selection)
      if not r == None:
        self.handle_attribute(edit,r)
      # Is it a field of model.
      r = re.search("(?P<indent>^\s*)(?P<field>field)\s*:.*$",line_for_selection)
      if not r == None:
        self.handle_model_helpers(edit,r, "# Fields")
      # Is it a association of model.
      r = re.search("(?P<indent>^\s*)(?P<association>has_many|has_one|belongs_to|has_and_belongs_to_many|embeds_one|embeds_many)\s*:.*$",line_for_selection)
      if not r == None:
        self.handle_model_helpers(edit,r, "# Associations")
      # Is it a validation of model.
      r = re.search("(?P<indent>^\s*)(?P<validation>validate(s!?)?|validates_presence_of|validates_absence_of)\s*:.*$",line_for_selection)
      if not r == None:
        self.handle_model_helpers(edit,r, "# Validations")
      # Is it a delegate set on model.
      r = re.search("(?P<indent>^\s*)(?P<delegate>delegate)\s*:.*$",line_for_selection)
      if not r == None:
        self.handle_model_helpers(edit,r, "# Delegate")

  # Number of tab variable positions for a single parameter.
  # The positions are type, name and description
  ARGS_FOR_PARAM = 3

  def handle_model_helpers(self,edit,r,helper_comment):
    self.indent = r.group("indent")
    self.lines = []
    self.lines.append(helper_comment)
    self.run_command(edit,self.concat())

  def handle_attribute(self,edit,r):
    self.indent = r.group("indent")
    if r.group("attribute") == "attr_reader":
      mode = "r"
    elif r.group("attribute") == "attr_writer":
      mode = "w"
    elif r.group("attribute") == "attr_accessor":
      mode = "rw"
    else:
      print("** Warning: Unknown attribute: '%s'" % r.group("attribute"))
    self.lines = []
    if(self.settings.get('initial_empty_line')):
      self.lines.append("#")
    self.lines.append("# @!attribute [%s] %s" % (mode,r.group("name")))
    self.lines.append("#   @return [%s] %s" % (self.tv("<type>"),self.tv("<description>")))
    self.run_command(edit,self.concat())

  def handle_module(self,edit,r):
    self.indent = r.group("indent")
    self.lines = []
    if(self.settings.get('initial_empty_line')):
      self.lines.append("#")
    self.lines.append("# %s %s provides %s" % (r.group("mod_or_class").capitalize(),r.group("name"),self.tv("<description>")))
    self.lines.append("#")
    if(self.settings.get('author')):
      username = self.settings.get('author')
    elif os.name == 'nt':
      username = os.environ['USERNAME']
    else:
      username = os.environ['USER']
    self.lines.append("# @author %s" % self.tv(username))
    self.lines.append("#")
    self.run_command(edit,self.concat())

  # Set the cursor to the left of the currrent line
  # or the line indicated by offset. Offset can be
  # negative.
  def cursor_to_the_left(self,offset=0):
    # Get the current position
    pos = self.view.sel()[0]
    # Convert to line/column number
    pt = self.view.rowcol(pos.begin())
    # Clear the current selection
    self.view.sel().clear()
    # And set the new position
    self.view.sel().add(self.view.text_point(pt[0]+offset,0))
    # Write the string to the system

  # Concatenate the lines array and return the string
  def concat(self):
    return self.indent + (self.line_ending() + self.indent).join(self.lines)

  # Tab variable. Return a string like: ${12:name} where
  # 12 is defined by self.count.
  # self.count is incremented.
  def tv(self,name):
    self.count += 1
    return "${" + str(self.count - 1) + ":" + name + "}"

  def handle_constant(self,edit,r):
    self.indent = r.group("indent")
    self.lines = []
    if(self.settings.get('initial_empty_line')):
      self.lines.append("#")
    self.lines.append("# @return [" + self.tv("<type>") + "] " + self.tv("<description>"))
    self.run_command(edit,self.concat())

  # Return the standard header for the method.
  # This is the method documentation, the
  # parameters documentation and the optional
  # return documentation.
  def method_documentation_header(self,r):
    self.lines = []
    # Start with an empty line
    if(self.settings.get('initial_empty_line')):
      self.lines.append("#")
    # Every method has a description
    self.lines.append("# " + self.tv("<description>"))
    # And another emty line
    self.lines.append("#")
    # Remember where the arguments start
    self.arg_start = self.count
    # Does the function have arguments?
    if r.group("args"):
      # Loop over each argument
      for param in r.group("args").split(","):
        # The param may have a assignment
        param = param.strip()
        p = re.search(r'^(.*?)\s*=.*$',param)
        if not p == None:
          param = p.group(1)
        # The param may have an ampersand to indicate a block
        p = re.search(r'^\s*&',param)
        if p == None:
          # Add a @param line
          self.lines.append("# @param " +
            "[" + self.tv("<type>") + "] " +
            self.tv(param) + " " +
            self.tv("<description>"))
    # All methods have a return except the initialize method
    if r.group("name") != "initialize":
      self.lines.append("#")
      self.lines.append("# @return [" + self.tv("<type>") +
        "] " + self.tv("<description>"))
    # An empty line between the params and the function
    self.lines.append("# ")
    # Get the indent
    self.indent = r.group("indent")
    # Convert the array to a string
    if self.debug_method:
      print(self.concat())
    return self.concat()

  def method_body_variable_substitution(self,method_body_region,args):
    # Add tabgroups to the body. This will allow us to change names
    # of variables in an easy way
    method_body = self.view.substr(method_body_region)
    # dollar signs need protection before we insert the tab variables
    method_body = re.sub(r'\$','\\$',method_body)
    self.count = self.arg_start + 1
    if not args == None:
      for param in args.split(","):
        # Check if the param has an assignment
        param = param.strip()
        r = re.search(r'^(.*?)\s*=.*$',param)
        if not r == None:
          param = r.group(1)
        # Check if the param is not a block
        r = re.search(r'^\s*&',param)
        if r == None:
          escaped_param = re.sub(r'\*',r'\\*',param)
          search = r'(\W)(%s)(\W)' % escaped_param
          repl = r'\1${%d:%s}\3' % (self.count,param)
          method_body = re.sub(search,repl,method_body)
          self.count += self.ARGS_FOR_PARAM
    if self.debug_method:
      print(method_body)
    return method_body

  def yield_param(self,param):
    return (
      "# @yieldparam [" + self.tv("<type>") +
            "] " + self.tv(param) +
            " " + self.tv("<description>")
    )

  def method_body_yield_detection(self,method_body_region,args):
    method_body = self.view.substr(method_body_region)
    self.lines = []
    r = re.search(self.yield_regex,method_body)
    if r != None:
      args = r.group("args")
      if args != None:
        for param in args.split(","):
          param = param.strip()
          if re.search(r'^[a-z][a-z0-9A-Z]*$',param):
            self.lines.append(self.yield_param(param))
          else:
            # Try to match a regular string from the parameter
            m = re.search(r'(?<=[\s(])([a-z][a-z0-9A-Z]*)',param)
            if m:
              self.lines.append(self.yield_param(m.group(1)))
            else:
              self.lines.append(self.yield_param("x"))
      self.lines.append("# @yieldreturn [" + self.tv("<type>") +
        "] " + self.tv("<describe what yield should return>"))
      if self.debug_method:
        print(self.concat())
      return self.concat()
    else:
      if self.debug_method:
        print("Checking for block argument")
      if not args == None:
        # Check if the args have a block argument
        for param in args.split(","):
          # Check for a block argument
          r = re.search(r'^\s*&',param)
          if not r == None:
            self.lines.append("# @yield " + self.tv("<description>"))
            self.lines.append("#")
            if self.debug_method:
              print("Return yield block argument: " + self.concat())
            return self.concat()
      # Did not find any block param
      if self.debug_method:
        print("No yield data")
      return ""

  def handle_method(self,edit,selection,r):    # Build up the end result in an array
    data = self.method_documentation_header(r)
    method_body_region = self.full_method_body(selection)
    method_body_yield = self.method_body_yield_detection(method_body_region,r.group("args"))
    if len(method_body_yield)>0:
      data += "\n"
      data += method_body_yield
    method_body = self.method_body_variable_substitution(method_body_region,r.group("args"))
    data += self.line_ending()
    data += method_body
    self.view.erase(edit,method_body_region)
    self.run_command(edit,data.rstrip("\n\r"))
