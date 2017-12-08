# YardGenPlus: Yard generator integration for Sublime Text 3

##### Cloned from Fred Appelman's [Yardgen](https://bitbucket.org/fappelman/yardgen)

**Author**: John Schulz

**License**: MIT License

**Email**: johnschulz75@gmail.com

## Suggestions, questions or issues?

If you have questions, suggestions or issues with this software please let me know by adding an issue.

## Synopsis

Yard generator is a plugin for Sublime Text that will generate inline [Yard](https://github.com/lsegal/yard) documentation for Ruby source code. _Yard_ will then convert this into a proper HTML documentation set.

Simply spoken you position the cursor on the method, class, module attribute, etc. that you want to document and hit **_CTRL+Return_** and a documentation template will be added. Next you can tab through the template and write the actual documentation within the template. It prevents the tedious part of remembering the exact format of the documentation. The goals is to be as complete as possible when generating documentation. So that you end up with 100% documentation coverage without warnings.

It even allows you to rename you method parameters during this phase. If you are like me your parameter names may not fully cover the function any more by the time you finished writing your software.

In the case you want to add additional documentation you can use tab completion to insert the _Yard_ constructs manually.

![Yardgen in action(YardGenPlus looks the same, but with more options)](https://bitbucket.org/fappelman/yardgen/wiki/demo.gif)

## Compatibility

This package has been tested with ST3 but there is not reason it should not work with ST2 as well.

## Inspiration

##### from [Yardgen README](https://bitbucket.org/fappelman/yardgen/README.md)

> The initial inspiration came from the yardoc package [sublime-yardoc](http://revathskumar.github.com/sublime-yardoc/) written by [revathskumar](https://github.com/revathskumar) and from the the yardoc package found in [TextMate](http://macromates.com/). The tab completions I shamelessly copied from _revathskumar_.

> The package created by _revathskumar_ simply didn't provide enough features for my taste, hence this package.

Yardgen simply didn't provide enough features for my taste, hence _this_ package.

## Installation

### With Package Control (currently unavailable)

<!--

The easiest way to install this is with [Package Control](http://wbond.net/sublime_packages/package_control).

* If you just went and installed Package Control, you probably need to restart Sublime Text 3 before doing this next bit.
* Bring up the Command Palette (Command+Shift+p on OS X, Control+Shift+p on Linux/Windows).
* Select “Package Control: Install Package” (it'll take a few seconds)
* Select YardGenPlus when the list appears.
* Package Control will automatically keep YardGenPlus up to date with the latest version.
-->

### Without Package Control

Go to your _Sublime Text_ **Packages** directory `(Sublime Text -> Preferences -> Browse Packages...)`
and clone the repository using the command below:

    git clone git@github.com:nimylian/YardGenPlus.git

From time to time you can issue the update command in the yardgen directory:

    git pull

This will update you to the latest version.

## Usage

Press **ctrl+enter** on the method definition:

    def simple_method
      # Method body
    end

will result in:

    # <description>
    #
    # @return [<type>] <description>
    def simple_method
      # Method body
    end

## Feature List

#### Module

    module Example
    end

will expand into:

    # Module Example provides <description>
    #
    # @author Joe Blog <Joe.Blog@nowhere.com>
    module Example
    end

where the author can be set in the settings file. If not defined the USER environment variable will be used.

#### Class

    class Example
    end

will expand into:

    # Class Example provides <description>
    #
    # @author Joe Blog <Joe.Blog@nowhere.com>
    module Class
    end

#### Constructor (initialize)

The constructor is special as it does not require a return type, _Yard_ already knows how to handle this method:

    def initialize(a,b)
    end

will expand into:

    # <description>
    #
    # @param  [<type>] a <description>
    # @param  [<type>] b <description>
    def initialize(a,b)
    end

#### A normal (class) method

    def normal_method(a,b)
    end

will expand into:

    # <description>
    #
    # @param  [<type>] a <description>
    # @param  [<type>] b <description>
    # @return [<type>] <description>
    def normal_method(a,b)
    end

#### A read only attribe

    attr_reader :read_only_attr

will expand into:

    # @!attribute [r] read
    #   @return [<type] <description>
    attr_reader :read_only_attr

#### A read/write attribute

    attr_accessor :read_write_attr

will expand into:

    # @!attribute [rw] read
    #   @return [<type] <description>
    attr_accessor :read_write_attr

#### A write only attribute

    attr_writer :write_only_attr

will expand into:

    # @!attribute [w] write
    #   @return [<type] <description>
    attr_writer :write_only_attr

#### Constant

    CONSTANT="123"

will expand into:

    # @return [<type>] <description>
    CONSTANT="123"

#### A method that yields

    def method
      yield a,b
    end

will epxand into:

    # <description>
    #
    # @return [<type>] <description>
    # @yieldparam [<type>] a <description>
    # @yieldparam [<type>] b <description>
    # @yieldreturn [<type>] <describe what yield should return>
    def method
      yield a,b
    end

If the yield doesn't pass parameters only the _@yieldreturn_ will be present.

#### Rails

Some limited rails functionality is provided. The `field` keyword is recognized.

    class RailsExample

field :ab

    end

will expand into:

    class RailsExample

      # Fields
      field :ab

    end

The Associations `has_many`, `has_one`, `belongs_to`, `has_and_belongs_to_many`, `embeds_one`, `embeds_many` will add the
comment 'Associations'.

For example:

    class RailsExample

      has_many :ab

    end

will expand into:

    class RailsExample

      # Associations
      has_many :ab

    end

The keyword `delegate` will add the comment 'Delegate'.

For example:

    class RailsExample

      delegate :name, :to => :user

    end

will expand into:

    class RailsExample

      # Delegate
      delegate :name, :to => :user

    end

And finally the validations `validate`, `validates`, `validates_presence_of`, `validates_absence_of` will add the
comment 'Validations'.

For example:

    class RailsExample

      validate :ab

    end

will expand into:

    class RailsExample

      # Validations
      validate :ab

    end

## Tabcompletions

The following list of tab completions is present:

* @abstract

* @api

* @attr

* @attr_reader

* @attr_writer

* @author

* @deprecated

* @example

* @note

* @option

* @overload

* @param

* @private

* @raise

* @return

* @see

* @since

* @todo

* @version

* @yield

* @yieldparam

* @yieldreturn

## Default Settings

##### To change these, override them in the file at `Sublime Text -> Preferences -> Package Settings -> Yardgen -> Settings-User`

    // Specify the @author. If not defined it will default to
    // the login name through the environment variable USER
    "author": "Joe Blog <Joe.Blog@nowhere.com>"
    // Add an initial empty line at the beginning of the comment
    "initial_empty_line": false
    // Add an empty line after the author
    "line_after_author": false
    // Add an empty line after the description
    "line_after_description": true
    // Add an empty line after a yield
    "line_after_yield": false
    // Add an empty line before the return
    "line_before_return": false
    // Add an empty line after the return
    "line_after_return": false

## License

The MIT License (MIT)
Copyright (c) 2017 John Schulz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
